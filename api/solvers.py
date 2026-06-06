"""Solver wrappers for the OptiLoc API.

Loads the numbered notebook scripts (files 08 and 16) as modules via
importlib.util — the same pattern Session 013 used in file 18 to reuse
file 16's Lloyd machinery. Notebooks remain the single source of truth for
solver math.

Road-network solvers (Weber + k-median) are implemented directly here;
their graph and aggregated demand data are cached at startup alongside
the Euclidean assets.

Data assets are loaded once into a process-wide cache at startup via
initialize_solvers(), then reused across requests.
"""

import importlib.util
import time
from types import ModuleType

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd

from api.config import (
    BUFFER_DEG,
    DEMAND_CSV,
    KMEDIAN_SOLVER_PATH,
    OZP_GEOJSON,
    ROAD_AGG_CSV,
    ROAD_GRAPH_ML,
    ROAD_KMEDIAN_MAX_ITERS,
    RNG_SEED,
    WEBER_SOLVER_PATH,
    WEISZFELD_START_LAT,
    WEISZFELD_START_LON,
)


# ---- importlib module loader --------------------------------------------------

def _load_module_from_path(name: str, path) -> ModuleType:
    """Load a Python file as a module; needed because notebook files start
    with digits (e.g. '08_solve_weber_weiszfeld.py') which can't be regular
    imports. Same pattern as notebooks/18_ksweep_ozp.py."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---- Process-wide cache -------------------------------------------------------
# Euclidean solvers (populated by initialize_solvers).
_weber_mod: ModuleType | None = None
_kmedian_mod: ModuleType | None = None
_demand_points: np.ndarray | None = None
_weights: np.ndarray | None = None
_ozp_geom = None  # Buffered shapely (Multi)Polygon.

# Road-network solvers (populated by initialize_solvers).
_road_graph: nx.Graph | None = None       # Undirected — used for Dijkstra.
_road_graph_dir = None                     # Directed — used for nearest_nodes snapping.
_agg_demand_nodes: list | None = None      # Road node IDs (unique snapped demand nodes).
_agg_weights: np.ndarray | None = None
_agg_lats: np.ndarray | None = None
_agg_lons: np.ndarray | None = None


def initialize_solvers() -> None:
    """Load notebook modules and data assets once. Called from FastAPI lifespan."""
    global _weber_mod, _kmedian_mod, _demand_points, _weights, _ozp_geom
    global _road_graph, _road_graph_dir, _agg_demand_nodes
    global _agg_weights, _agg_lats, _agg_lons

    # Euclidean solvers.
    _weber_mod = _load_module_from_path("weber_mod", WEBER_SOLVER_PATH)
    _kmedian_mod = _load_module_from_path("kmedian_mod", KMEDIAN_SOLVER_PATH)

    df = pd.read_csv(DEMAND_CSV)
    _demand_points = df[["lon", "lat"]].to_numpy(dtype=float)
    _weights = df["weight"].to_numpy(dtype=float)

    ozp_gdf = gpd.read_file(OZP_GEOJSON)
    _ozp_geom = ozp_gdf.iloc[0].geometry.buffer(BUFFER_DEG)

    # Road-network solvers.
    _road_graph_dir = ox.load_graphml(ROAD_GRAPH_ML)
    _road_graph = _road_graph_dir.to_undirected()

    agg = pd.read_csv(ROAD_AGG_CSV)
    _agg_demand_nodes = [int(n) for n in agg["road_node"].tolist()]
    _agg_weights = agg["weight"].values.astype(float)
    _agg_lats = agg["lat"].values.astype(float)
    _agg_lons = agg["lon"].values.astype(float)


# ---- /solve_weber wrapper -----------------------------------------------------

def solve_weber() -> dict:
    """Solve the single-facility Weber problem using the Weiszfeld algorithm.
    
    This function uses Euclidean distances and starts from a baked-in 
    Victoria Harbour location.
    
    Returns:
        dict: A dictionary containing the optimal longitude, latitude, 
        objective value (total weighted distance in degree-units), iterations, 
        runtime, and demand point counts.
    """
    assert _weber_mod is not None and _demand_points is not None
    x0 = np.array([WEISZFELD_START_LON, WEISZFELD_START_LAT])

    t0 = time.perf_counter()
    x_star, iters, _trail = _weber_mod.weiszfeld(_demand_points, _weights, x0)
    elapsed = time.perf_counter() - t0

    f_star = _weber_mod.objective(x_star, _demand_points, _weights)
    return {
        "lon": float(x_star[0]),
        "lat": float(x_star[1]),
        "objective": float(f_star),
        "iterations": int(iters),
        "runtime_s": elapsed,
        "n_demand_points": int(len(_demand_points)),
        "total_weight": float(_weights.sum()),
    }


# ---- /solve_kmedian_ozp wrapper -----------------------------------------------

def solve_kmedian_ozp(k: int, n_restarts: int) -> dict:
    """Solve the k-median problem with an OZP commercial-zone constraint.
    
    Uses Lloyd's algorithm with population-weighted centroid snapping, 
    running over n_restarts random initializations to find the best optimum.
    This function operates on Euclidean distances.
    
    Args:
        k (int): Number of facilities to locate.
        n_restarts (int): Number of random initializations.
        
    Returns:
        dict: A dictionary with the best objective, worst objective, gap percentage,
        the list of optimal facility coordinates, and summary metrics for all restarts.
    """
    assert (
        _kmedian_mod is not None
        and _demand_points is not None
        and _ozp_geom is not None
    )
    rng = np.random.default_rng(RNG_SEED)

    t0 = time.perf_counter()
    results = []
    for r in range(1, n_restarts + 1):
        res = _kmedian_mod.lloyd_one_restart(
            _demand_points, _weights, _ozp_geom, k, rng, r
        )
        results.append(res)
    total_t = time.perf_counter() - t0

    best = min(results, key=lambda r: r["final_obj"])
    best_obj = best["final_obj"]
    worst_obj = max(r["final_obj"] for r in results)
    gap_pct = 100.0 * (worst_obj - best_obj) / best_obj if best_obj > 0 else 0.0
    distinct = {round(r["final_obj"], 0) for r in results}

    return {
        "k": k,
        "n_restarts": n_restarts,
        "best_objective": float(best_obj),
        "worst_objective": float(worst_obj),
        "worst_best_gap_pct": float(gap_pct),
        "n_distinct_optima": len(distinct),
        "facilities": [
            {"lon": float(lon), "lat": float(lat)}
            for lon, lat in best["facilities"]
        ],
        "restarts": [
            {
                "restart_id": r["restart_id"],
                "final_obj": float(r["final_obj"]),
                "n_lloyd_iters": int(r["n_lloyd_iters"]),
                "converged": bool(r["converged"]),
                "slsqp_calls": int(r["slsqp_calls"]),
                "weiszfeld_calls": int(r["weiszfeld_calls"]),
            }
            for r in results
        ],
        "runtime_s": total_t,
    }


# ---- Road-network helpers (private) ------------------------------------------

_EUCLIDEAN_OPT_LAT = 22.33729   # Weiszfeld optimum from notebook 08.
_EUCLIDEAN_OPT_LON = 114.17071


def _road_objective(node: int) -> float:
    """Total weighted road distance from *node* to all aggregated demand nodes."""
    lengths = nx.single_source_dijkstra_path_length(
        _road_graph, node, weight="length"
    )
    return float(
        sum(
            _agg_weights[i] * lengths.get(_agg_demand_nodes[i], np.inf)
            for i in range(len(_agg_demand_nodes))
        )
    )


def _road_local_search(start: int) -> tuple[int, float, int]:
    """Hill-climb on graph neighbours until no improvement (max 500 steps)."""
    current = start
    current_obj = _road_objective(current)
    final_iter = 0
    for final_iter in range(1, 501):
        neighbours = list(_road_graph.neighbors(current))
        best_node = current
        best_obj = current_obj
        for nb in neighbours:
            obj = _road_objective(nb)
            if obj < best_obj:
                best_obj = obj
                best_node = nb
        if best_node == current:
            break
        current = best_node
        current_obj = best_obj
    return current, current_obj, final_iter


def _cluster_road_local_search(
    start: int,
    cluster_node_ids: list[int],
    cluster_weights: np.ndarray,
    max_steps: int = 20,
) -> tuple[int, float]:
    """Maranzana hill-climb minimising weighted road distance to a demand subset.

    Same structure as _road_local_search but evaluates the objective only over
    the given cluster.  Used as a post-Lloyd refinement in solve_kmedian_road
    and solve_kmedian_rent_road to escape centroid-snap local basins.
    """
    def _obj(node: int) -> float:
        lengths = nx.single_source_dijkstra_path_length(
            _road_graph, node, weight="length"
        )
        return float(
            sum(w * lengths.get(n, np.inf)
                for n, w in zip(cluster_node_ids, cluster_weights))
        )

    current = start
    current_obj = _obj(current)
    for _ in range(max_steps):
        best_node = current
        best_obj = current_obj
        for nb in _road_graph.neighbors(current):
            val = _obj(nb)
            if val < best_obj:
                best_obj = val
                best_node = nb
        if best_node == current:
            break
        current = best_node
        current_obj = best_obj
    return current, current_obj


# ---- /solve_weber_road wrapper ------------------------------------------------

def solve_weber_road() -> dict:
    """Solve the single-facility Weber problem using road-network distances.

    Uses a 3-seed local search for the discrete road-network optimum.
    Seeds include:
      1. Nearest road node to the Euclidean Weber optimum.
      2. Highest-weight aggregated demand node.
      3. 10th-highest-weight node (adds starting diversity).
      
    Returns:
        dict: The optimal road node ID, coordinates, total weighted road distance 
        (metres), per-resident distance, and runtime statistics.
    """
    assert (
        _road_graph is not None
        and _road_graph_dir is not None
        and _agg_demand_nodes is not None
    )

    seed1 = int(ox.nearest_nodes(_road_graph_dir, X=_EUCLIDEAN_OPT_LON, Y=_EUCLIDEAN_OPT_LAT))
    seed2 = int(_agg_demand_nodes[int(np.argmax(_agg_weights))])
    seed3 = int(_agg_demand_nodes[int(np.argsort(_agg_weights)[-10])])

    t0 = time.perf_counter()
    results = [_road_local_search(s) for s in (seed1, seed2, seed3)]
    elapsed = time.perf_counter() - t0

    best_node, best_obj, _ = min(results, key=lambda r: r[1])
    total_w = float(_agg_weights.sum())

    return {
        "node_id": int(best_node),
        "lon": float(_road_graph.nodes[best_node]["x"]),
        "lat": float(_road_graph.nodes[best_node]["y"]),
        "objective": float(best_obj),
        "per_resident_m": float(best_obj / total_w),
        "runtime_s": elapsed,
        "n_demand_nodes": len(_agg_demand_nodes),
        "total_weight": total_w,
    }


# ---- /solve_kmedian_road wrapper ---------------------------------------------

def solve_kmedian_road(k: int, n_restarts: int) -> dict:
    """Solve the k-median problem using road-network distances.

    Implements a multi-start Lloyd's algorithm where assignment is performed 
    via Dijkstra shortest-paths, and the location step uses a population-weighted 
    centroid snapped to the nearest road node.
    
    Args:
        k (int): Number of facilities to locate.
        n_restarts (int): Number of random initializations.
        
    Returns:
        dict: The best objective (metres), per-resident distance, worst objective, 
        and the final recommended facilities including their node IDs, coordinates, 
        and population served.
    """
    assert (
        _road_graph is not None
        and _road_graph_dir is not None
        and _agg_demand_nodes is not None
    )
    N = len(_agg_demand_nodes)
    total_w = float(_agg_weights.sum())
    rng = np.random.default_rng(RNG_SEED)

    t0 = time.perf_counter()
    restart_results = []

    for r in range(1, n_restarts + 1):
        seed = int(rng.integers(0, 2**31))
        fac_nodes = [
            int(n)
            for n in np.random.default_rng(seed).choice(
                _agg_demand_nodes, size=k, replace=False
            )
        ]
        prev_asgn = None
        dist_matrix = np.full((N, k), np.inf)

        for _it in range(1, ROAD_KMEDIAN_MAX_ITERS + 1):
            for j, fn in enumerate(fac_nodes):
                lengths = nx.single_source_dijkstra_path_length(
                    _road_graph, fn, weight="length"
                )
                dist_matrix[:, j] = [
                    lengths.get(dn, np.inf) for dn in _agg_demand_nodes
                ]

            asgn = dist_matrix.argmin(axis=1)
            if prev_asgn is not None and np.array_equal(asgn, prev_asgn):
                break
            prev_asgn = asgn.copy()

            new_fac = []
            for j in range(k):
                mask = asgn == j
                if not mask.any():
                    new_fac.append(fac_nodes[j])
                    continue
                w_j = _agg_weights[mask]
                tot = w_j.sum()
                c_lat = (w_j * _agg_lats[mask]).sum() / tot
                c_lon = (w_j * _agg_lons[mask]).sum() / tot
                new_fac.append(int(ox.nearest_nodes(_road_graph_dir, X=c_lon, Y=c_lat)))
            fac_nodes = new_fac

        # Post-Lloyd Maranzana refinement: escape the centroid-snap local basin.
        for j in range(k):
            mask = asgn == j
            if not mask.any():
                continue
            c_node_ids = [_agg_demand_nodes[i] for i in np.where(mask)[0]]
            c_weights = _agg_weights[mask]
            fac_nodes[j] = _cluster_road_local_search(
                fac_nodes[j], c_node_ids, c_weights
            )[0]

        # Recompute distances and assignment with refined positions.
        for j, fn in enumerate(fac_nodes):
            lengths = nx.single_source_dijkstra_path_length(
                _road_graph, fn, weight="length"
            )
            dist_matrix[:, j] = [
                lengths.get(dn, np.inf) for dn in _agg_demand_nodes
            ]
        asgn = dist_matrix.argmin(axis=1)

        obj = float((_agg_weights * dist_matrix[np.arange(N), asgn]).sum())
        restart_results.append(
            {"restart_id": r, "fac_nodes": fac_nodes, "asgn": asgn, "final_obj": obj}
        )

    elapsed = time.perf_counter() - t0
    best = min(restart_results, key=lambda r: r["final_obj"])
    best_obj = best["final_obj"]
    worst_obj = max(r["final_obj"] for r in restart_results)
    gap_pct = 100.0 * (worst_obj - best_obj) / best_obj if best_obj > 0 else 0.0
    distinct = {round(r["final_obj"], 0) for r in restart_results}

    facilities = []
    for j, fn in enumerate(best["fac_nodes"]):
        mask = best["asgn"] == j
        pop = float(_agg_weights[mask].sum())
        facilities.append(
            {
                "node_id": int(fn),
                "lon": float(_road_graph.nodes[fn]["x"]),
                "lat": float(_road_graph.nodes[fn]["y"]),
                "population_served": pop,
                "pct_served": float(100.0 * pop / total_w),
            }
        )

    return {
        "k": k,
        "n_restarts": n_restarts,
        "best_objective": float(best_obj),
        "per_resident_m": float(best_obj / total_w),
        "worst_objective": float(worst_obj),
        "worst_best_gap_pct": float(gap_pct),
        "n_distinct_optima": len(distinct),
        "facilities": facilities,
        "runtime_s": elapsed,
        "n_demand_nodes": N,
        "total_weight": total_w,
    }

# ---- /analyze_network wrapper ------------------------------------------------

def analyze_network(
    existing_locations: list[tuple[float, float]],
    k: int,
    n_restarts: int,
) -> dict:
    """Baseline-aware network audit.

    Parameters
    ----------
    existing_locations : list of (lat, lon) pairs — caller's current facilities.
    k                  : number of facilities to optimise for.
    n_restarts         : multi-start count passed to k-median solver.

    Returns
    -------
    dict matching AnalyzeNetworkResponse.
    """
    assert (
        _road_graph is not None
        and _road_graph_dir is not None
        and _agg_demand_nodes is not None
    )

    N = len(_agg_demand_nodes)
    total_w = float(_agg_weights.sum())

    t0 = time.perf_counter()

    # --- 1. Snap existing locations to nearest road nodes ---------------------
    # existing_locations are (lat, lon); ox.nearest_nodes wants X=lon, Y=lat.
    existing_nodes = [
        int(ox.nearest_nodes(_road_graph_dir, X=lon, Y=lat))
        for lat, lon in existing_locations
    ]

    # --- 2. Compute baseline objective ----------------------------------------
    m = len(existing_nodes)
    baseline_dist = np.full((N, m), np.inf)
    for j, fn in enumerate(existing_nodes):
        lengths = nx.single_source_dijkstra_path_length(
            _road_graph, fn, weight="length"
        )
        baseline_dist[:, j] = [
            lengths.get(dn, np.inf) for dn in _agg_demand_nodes
        ]

    baseline_asgn = baseline_dist.argmin(axis=1)
    baseline_obj = float(
        (_agg_weights * baseline_dist[np.arange(N), baseline_asgn]).sum()
    )

    # --- 3. Run k-median solver for optimal -----------------------------------
    optimal = solve_kmedian_road(k, n_restarts)

    elapsed = time.perf_counter() - t0

    # --- 4. Compute improvement -----------------------------------------------
    optimal_obj = optimal["best_objective"]
    improvement_pct = (
        100.0 * (baseline_obj - optimal_obj) / baseline_obj
        if baseline_obj > 0 else 0.0
    )

    return {
        "k": k,
        "baseline_objective": baseline_obj,
        "optimal_objective": optimal_obj,
        "improvement_pct": improvement_pct,
        "baseline_per_resident_m": baseline_obj / total_w,
        "optimal_per_resident_m": optimal_obj / total_w,
        "recommended_facilities": optimal["facilities"],
        "runtime_s": elapsed,
        "n_demand_nodes": N,
        "total_weight": total_w,
    }