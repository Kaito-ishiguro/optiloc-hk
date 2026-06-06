"""Travel-time routing layer for OptiLoc HK.

Adds free-flow edge speeds and travel times to the existing osmnx road graph
using osmnx's built-in speed imputation, then exposes metric="time" as an
opt-in alternative to metric="distance" (weight="length") in coverage and
1-median calculations.

NOT wired into live API endpoints in this session. Import from validation
scripts or notebooks only. The existing distance path and all production
endpoint behaviour are unchanged.

Phase 1a: free-flow speeds (osmnx imputation — no external data).
Phase 1b (pending): congestion overlay from data.gov.hk traffic detectors.

Usage
-----
    G_dir = ox.load_graphml(ROAD_GRAPH_ML)
    augment_graph_with_travel_times(G_dir)   # in-place, adds speed_kph + travel_time
    G = G_dir.to_undirected()                # Dijkstra graph for both metrics

    # Distance mode (identical to existing production code):
    result = coverage_analysis(G, G_dir, branch_coords, demand_nodes, weights,
                               metric="distance")

    # Time mode (new):
    result = coverage_analysis(G, G_dir, branch_coords, demand_nodes, weights,
                               metric="time")
"""

from __future__ import annotations

import logging
from typing import Literal

import networkx as nx
import numpy as np
import osmnx as ox

log = logging.getLogger(__name__)

# Maps metric name to the edge attribute used in Dijkstra.
WEIGHT_KEY: dict[str, str] = {
    "distance": "length",       # metres — always present on osmnx edges
    "time": "travel_time",      # seconds — added by augment_graph_with_travel_times()
    "time_peak": "travel_time_peak",  # seconds — Phase 1b congestion overlay (not yet built)
}

Metric = Literal["distance", "time", "time_peak"]


# ── Phase 1a: graph augmentation ───────────────────────────────────────────────

def augment_graph_with_travel_times(G_dir) -> dict:
    """Add speed_kph and travel_time (seconds) to every edge of G_dir in-place.

    Uses osmnx's two-step imputation:
      1. ox.add_edge_speeds: reads maxspeed OSM tag where present; falls back to
         highway-type mean from osmnx's built-in lookup table.
      2. ox.add_edge_travel_times: travel_time = length / (speed_kph / 3.6).

    Never falls back silently to a length-only estimate — edges with no OSM
    speed tag receive the documented highway-type mean (auditable, not zero).
    The "length" attribute is not modified, so distance-mode Dijkstra is
    unaffected.

    Returns a coverage summary dict for logging and validation.
    """
    ox.add_edge_speeds(G_dir)        # adds speed_kph
    ox.add_edge_travel_times(G_dir)  # adds travel_time

    edges = [(u, v, k, d) for u, v, k, d in G_dir.edges(keys=True, data=True)]
    n_total = len(edges)
    n_has_maxspeed = sum(
        1 for _, _, _, d in edges
        if "maxspeed" in d and d["maxspeed"] is not None
    )
    n_imputed = n_total - n_has_maxspeed
    speeds = [d["speed_kph"] for _, _, _, d in edges]
    travel_times = [d["travel_time"] for _, _, _, d in edges]

    summary = {
        "n_edges": n_total,
        "n_with_observed_maxspeed": n_has_maxspeed,
        "n_imputed_from_highway_type": n_imputed,
        "pct_imputed": 100.0 * n_imputed / n_total if n_total else 0.0,
        "speed_kph_min": float(min(speeds)),
        "speed_kph_mean": float(np.mean(speeds)),
        "speed_kph_max": float(max(speeds)),
        "travel_time_s_min": float(min(travel_times)),
        "travel_time_s_mean": float(np.mean(travel_times)),
        "travel_time_s_max": float(max(travel_times)),
    }
    log.info(
        "augment_graph_with_travel_times: %d edges, %d with observed maxspeed "
        "(%.1f%% imputed from highway type)",
        n_total, n_has_maxspeed, summary["pct_imputed"],
    )
    return summary


# ── Core routing helpers ────────────────────────────────────────────────────────

def dijkstra_from_node(G, source: int, metric: Metric = "distance") -> dict[int, float]:
    """Single-source Dijkstra from *source*. Returns {node: metres | seconds}."""
    weight = WEIGHT_KEY[metric]
    return dict(nx.single_source_dijkstra_path_length(G, source, weight=weight))


# ── Coverage analysis ───────────────────────────────────────────────────────────

# Default thresholds per metric — used for "underserved" classification.
_THRESHOLD: dict[str, float] = {
    "distance": 3_000.0,    # 3 km road distance (matches existing audit scripts)
    "time": 15 * 60.0,      # 15 minutes free-flow travel time
    "time_peak": 20 * 60.0, # 20 minutes peak travel time (Phase 1b)
}


def coverage_analysis(
    G,
    G_dir,
    branch_coords: list[tuple[float, float]],  # (lat, lon) pairs
    demand_nodes: list[int],
    demand_weights: np.ndarray,
    metric: Metric = "distance",
    threshold: float | None = None,
) -> dict:
    """Coverage analysis with selectable metric.

    When metric="distance", this is a drop-in replacement for the existing
    audit step2 scripts (same Dijkstra engine, same weight="length").

    Parameters
    ----------
    G            : undirected road graph (from G_dir.to_undirected())
    G_dir        : directed graph for nearest_nodes snapping
    branch_coords: list of (lat, lon) tuples for each facility
    demand_nodes : snapped osmnx node IDs
    demand_weights: population weights matching demand_nodes
    metric       : "distance" | "time" | "time_peak"
    threshold    : underserved cutoff in metric units; defaults to _THRESHOLD[metric]

    Returns
    -------
    dict with:
      metric, unit, threshold,
      wtd_mean         — population-weighted mean (m or s)
      pct_underserved  — % of population beyond threshold
      branch_nodes     — snapped node IDs
      dist_matrix      — (n_branches × n_demand) array of raw values
      nearest          — per-demand minimum across branches
    """
    if threshold is None:
        threshold = _THRESHOLD[metric]
    weight = WEIGHT_KEY[metric]
    unit = "m" if metric == "distance" else "s"

    branch_nodes = [
        int(ox.nearest_nodes(G_dir, X=lon, Y=lat))
        for lat, lon in branch_coords
    ]

    N = len(demand_nodes)
    B = len(branch_nodes)
    dist_matrix = np.full((B, N), np.inf)

    for i, b_node in enumerate(branch_nodes):
        lengths = dijkstra_from_node(G, b_node, metric=metric)
        for j, d_node in enumerate(demand_nodes):
            dist_matrix[i, j] = lengths.get(d_node, np.inf)

    nearest = dist_matrix.min(axis=0)
    reachable = np.isfinite(nearest)
    d = nearest[reachable]
    w = demand_weights[reachable]
    total_w = demand_weights.sum()

    wtd_mean = float(np.average(d, weights=w))
    underserved_pop = float(w[d > threshold].sum())

    return {
        "metric": metric,
        "unit": unit,
        "threshold": threshold,
        "wtd_mean": wtd_mean,
        "pct_underserved": 100.0 * underserved_pop / total_w,
        "branch_nodes": branch_nodes,
        "dist_matrix": dist_matrix,
        "nearest": nearest,
    }


# ── Road 1-median ───────────────────────────────────────────────────────────────

def road_1median(
    G,
    G_dir,
    demand_nodes: list[int],
    demand_weights: np.ndarray,
    demand_lats: np.ndarray,
    demand_lons: np.ndarray,
    metric: Metric = "distance",
    n_seeds: int = 3,
) -> dict:
    """Road-network 1-median via multi-seed local search.

    Mirrors solve_weber_road from api/solvers.py but accepts metric="time".
    Seeds: (1) population centroid snapped to nearest node, (2) highest-weight
    demand node, (3) 10th-highest-weight demand node.

    NOTE: this runs one full Dijkstra per neighbor per local-search step, which
    is slow for large graphs. For the Phase 1a validation, prefer coverage_analysis
    (6 Dijkstra runs from branches) over this function.
    """
    weight = WEIGHT_KEY[metric]
    total_w = float(demand_weights.sum())

    def objective(node: int) -> float:
        lengths = dijkstra_from_node(G, node, metric=metric)
        return float(sum(
            demand_weights[i] * lengths.get(demand_nodes[i], np.inf)
            for i in range(len(demand_nodes))
        ))

    def local_search(start: int) -> tuple[int, float, int]:
        cur, cur_obj = start, objective(start)
        steps = 0
        for steps in range(1, 501):
            best_nb, best_obj = cur, cur_obj
            for nb in G.neighbors(cur):
                o = objective(nb)
                if o < best_obj:
                    best_obj, best_nb = o, nb
            if best_nb == cur:
                break
            cur, cur_obj = best_nb, best_obj
        return cur, cur_obj, steps

    c_lat = float(np.average(demand_lats, weights=demand_weights))
    c_lon = float(np.average(demand_lons, weights=demand_weights))
    seed1 = int(ox.nearest_nodes(G_dir, X=c_lon, Y=c_lat))
    seed2 = int(demand_nodes[int(np.argmax(demand_weights))])
    seed3 = int(demand_nodes[int(np.argsort(demand_weights)[-10])])

    results = [local_search(s) for s in (seed1, seed2, seed3)[:n_seeds]]
    best_node, best_obj, best_steps = min(results, key=lambda r: r[1])

    return {
        "metric": metric,
        "unit": "m" if metric == "distance" else "s",
        "node_id": int(best_node),
        "lon": float(G.nodes[best_node]["x"]),
        "lat": float(G.nodes[best_node]["y"]),
        "objective": float(best_obj),
        "per_resident": float(best_obj / total_w),
        "local_search_steps": int(best_steps),
        "n_seeds": n_seeds,
    }
