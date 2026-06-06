"""Competitor coverage analysis for OptiLoc HK.

Compares an operator's facility network against a competitor network using
road-network distances (multi-source Dijkstra), classifies each demand node
by who is closer, quantifies at-risk demand, and optionally recommends a new
site via Maranzana local search on the at-risk subset only.

Never falls back to Euclidean distances or centroid approximations.
Raises RuntimeError if the shared graph cache is not initialised.
"""

from __future__ import annotations

import logging

import networkx as nx
import numpy as np
import osmnx as ox

import api.solvers as _solvers

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Graph / demand access helpers
# ---------------------------------------------------------------------------

def _require_graph() -> None:
    if _solvers._road_graph is None or _solvers._road_graph_dir is None:
        raise RuntimeError(
            "Road graph not initialised. Call initialize_solvers() at startup."
        )


def snap_locations(latlng_list: list[list[float]]) -> list[int]:
    """Snap (lat, lng) pairs to nearest road-graph nodes.

    Parameters
    ----------
    latlng_list : list of [lat, lng] pairs

    Returns
    -------
    list of osmnx node IDs (int), one per input location
    """
    _require_graph()
    G_dir = _solvers._road_graph_dir
    return [
        int(ox.nearest_nodes(G_dir, X=lng, Y=lat))
        for lat, lng in latlng_list
    ]


def multi_source_dijkstra(source_nodes: list[int]) -> dict[int, float]:
    """Road-network shortest path length from any source node to all graph nodes.

    Uses nx.multi_source_dijkstra_path_length — one Dijkstra pass from the
    combined source set, not a per-source loop.

    Parameters
    ----------
    source_nodes : snapped node IDs for the facility set

    Returns
    -------
    dict {node_id: distance_m} — nodes unreachable from all sources are absent;
    callers should use .get(node, inf) when looking up individual nodes.
    """
    _require_graph()
    G = _solvers._road_graph
    return dict(
        nx.multi_source_dijkstra_path_length(G, set(source_nodes), weight="length")
    )


# ---------------------------------------------------------------------------
# Classification and aggregation
# ---------------------------------------------------------------------------

def _classify_demand_nodes(
    demand_nodes: list[int],
    d_operator: dict[int, float],
    d_competitor: dict[int, float],
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Classify each demand node into a coverage zone.

    Zones
    -----
    "operator_wins"   — d_op <= d_comp (equidistant counts as operator)
    "competitor_wins" — d_comp < d_op (competitor is strictly closer)
    "neither"         — both distances are inf (unreachable from both networks)

    Returns (zones, op_dists, comp_dists) as parallel arrays.
    """
    n = len(demand_nodes)
    op_dists = np.full(n, np.inf)
    comp_dists = np.full(n, np.inf)
    zones: list[str] = []

    for i, node in enumerate(demand_nodes):
        d_op = d_operator.get(node, np.inf)
        d_comp = d_competitor.get(node, np.inf)
        op_dists[i] = d_op
        comp_dists[i] = d_comp

        if np.isinf(d_op) and np.isinf(d_comp):
            zones.append("neither")
        elif d_comp < d_op:
            zones.append("competitor_wins")
        else:
            zones.append("operator_wins")

    return zones, op_dists, comp_dists


# ---------------------------------------------------------------------------
# At-risk 1-median (Maranzana local search on at-risk subset)
# ---------------------------------------------------------------------------

def compute_at_risk_1median(
    at_risk_nodes: list[int],
    at_risk_weights: np.ndarray,
    n_restarts: int = 3,
) -> dict | None:
    """Road-network 1-median for the at-risk demand subset.

    Seeds are the top n_restarts highest-weight at-risk nodes.  Each seed
    runs Maranzana local search (best-improving neighbour, up to 500 steps).
    Best result across restarts is returned.

    Parameters
    ----------
    at_risk_nodes   : graph node IDs for competitor_wins demand nodes
    at_risk_weights : population weights matching at_risk_nodes
    n_restarts      : number of seeds (default 3)

    Returns
    -------
    dict with node_id, lat, lng, at_risk_mean_distance_m — or None if the
    at-risk set is empty.
    """
    if len(at_risk_nodes) == 0:
        return None

    _require_graph()
    G = _solvers._road_graph
    total_w = float(at_risk_weights.sum())

    def objective(node: int) -> float:
        lengths = dict(nx.single_source_dijkstra_path_length(G, node, weight="length"))
        return float(sum(
            at_risk_weights[i] * lengths.get(at_risk_nodes[i], np.inf)
            for i in range(len(at_risk_nodes))
        ))

    def local_search(start: int) -> tuple[int, float]:
        cur, cur_obj = start, objective(start)
        for _ in range(500):
            best_nb, best_obj = cur, cur_obj
            for nb in G.neighbors(cur):
                o = objective(nb)
                if o < best_obj:
                    best_obj, best_nb = o, nb
            if best_nb == cur:
                break
            cur, cur_obj = best_nb, best_obj
        return cur, cur_obj

    top_idx = np.argsort(at_risk_weights)[::-1][:n_restarts]
    seeds = [at_risk_nodes[i] for i in top_idx]

    best_node, best_obj = None, np.inf
    for seed in seeds:
        node, obj = local_search(seed)
        if obj < best_obj:
            best_obj, best_node = obj, node

    mean_distance_m = best_obj / total_w if total_w > 0 else 0.0
    log.info(
        "at_risk_1median: best_node=%d, mean_distance_m=%.1f, n_at_risk=%d",
        best_node, mean_distance_m, len(at_risk_nodes),
    )

    return {
        "node_id": int(best_node),
        "lat": float(G.nodes[best_node]["y"]),
        "lng": float(G.nodes[best_node]["x"]),
        "at_risk_mean_distance_m": round(mean_distance_m, 2),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_competitor_coverage(
    operator_locations: list[list[float]],
    competitor_locations: list[list[float]],
    threshold_m: float,
    recommend_site: bool,
) -> dict:
    """Full competitor coverage analysis.

    Two multi-source Dijkstra runs (operator, competitor) on the shared
    road graph, then demand-node classification, aggregation, and optional
    at-risk 1-median recommendation.

    Never falls back to Euclidean distances or centroid approximations.
    """
    _require_graph()
    demand_nodes: list[int] = _solvers._agg_demand_nodes
    demand_weights: np.ndarray = _solvers._agg_weights
    total_w = float(demand_weights.sum())

    op_nodes = snap_locations(operator_locations)
    comp_nodes = snap_locations(competitor_locations)
    log.info(
        "Snapped %d operator locations, %d competitor locations",
        len(op_nodes), len(comp_nodes),
    )

    d_op = multi_source_dijkstra(op_nodes)
    log.info("Operator Dijkstra: %d reachable nodes", len(d_op))

    d_comp = multi_source_dijkstra(comp_nodes)
    log.info("Competitor Dijkstra: %d reachable nodes", len(d_comp))

    zones, op_dists, comp_dists = _classify_demand_nodes(demand_nodes, d_op, d_comp)
    zones_arr = np.array(zones)

    # At-risk demand (competitor_wins)
    at_risk_mask = zones_arr == "competitor_wins"
    at_risk_w = float(demand_weights[at_risk_mask].sum())

    # Population-weighted mean distances over all demand (finite only)
    op_finite = np.isfinite(op_dists)
    comp_finite = np.isfinite(comp_dists)
    op_mean = (
        float(np.average(op_dists[op_finite], weights=demand_weights[op_finite]))
        if op_finite.any() else 0.0
    )
    comp_mean = (
        float(np.average(comp_dists[comp_finite], weights=demand_weights[comp_finite]))
        if comp_finite.any() else 0.0
    )

    # Zone statistics
    zone_stats: dict[str, dict] = {}
    for zn in ("operator_wins", "competitor_wins", "neither"):
        mask = zones_arr == zn
        w = float(demand_weights[mask].sum())
        zone_stats[zn] = {
            "demand_pct": round(100.0 * w / total_w, 2),
            "resident_count": int(round(w)),
        }

    # Optional at-risk 1-median recommendation
    recommended_site = None
    if recommend_site:
        at_risk_indices = np.where(at_risk_mask)[0]
        if len(at_risk_indices) > 0:
            ar_nodes = [demand_nodes[i] for i in at_risk_indices]
            ar_weights = demand_weights[at_risk_indices]
            recommended_site = compute_at_risk_1median(ar_nodes, ar_weights)

    return {
        "at_risk_demand_pct": round(100.0 * at_risk_w / total_w, 2),
        "at_risk_resident_count": int(round(at_risk_w)),
        "operator_mean_distance_m": round(op_mean, 2),
        "competitor_mean_distance_m": round(comp_mean, 2),
        "zones": zone_stats,
        "recommended_site": recommended_site,
    }
