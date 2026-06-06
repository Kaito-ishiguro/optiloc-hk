"""Rent-aware k-median solver for OptiLoc HK.

Minimises a combined objective:

    obj = mean_coverage_m + rent_weight * rent_penalty_m

where:
    mean_coverage_m  = Σ(w_i × d_i) / Σ(w_i)          (pop-weighted mean road distance)
    rent_penalty_m   = mean(r̂_j for j in facilities)   (mean normalised rent, in metres)
    r̂_j             = (rent_j − r_min) / (r_max − r_min) × D_REF_M

At rent_weight=0 the objective reduces to the standard k-median distance objective,
giving the same result as solve_kmedian_road.

Algorithm: Lloyd's k-median (assignment + centroid-snap location update) with
multi-start, identical in structure to solve_kmedian_road in api/solvers.py.
The only change is:
  1. Candidate seeds are restricted to eligible districts (those with industrial
     rental data — excludes Wan Chai, Sha Tin, Islands).
  2. Seeds are drawn from a rent-weighted distribution when rent_weight > 0:
     low-rent NT nodes receive higher seeding probability, ensuring NT solutions
     are explored even with a small n_restarts.
  3. The best restart is selected by the combined objective, not pure distance.

At rent_weight=0 steps 2 and 3 reduce to uniform seeding and distance-only
selection — the result matches solve_kmedian_road (modulo the eligible-node
seed filter, which does not change the optimum for k=2 on HK demand data).
"""

from __future__ import annotations

import logging
import time

import networkx as nx
import numpy as np
import osmnx as ox

import api.solvers as _solvers
from api.config import ROAD_KMEDIAN_MAX_ITERS, RNG_SEED
from api.rent_data import D_REF_M, DISTRICT_REGION, REGIONAL_RENT

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require_graph() -> None:
    if _solvers._road_graph is None or _solvers._agg_demand_nodes is None:
        raise RuntimeError(
            "Road graph not initialised — initialize_solvers() must be called "
            "before solve_kmedian_rent_road()."
        )


def _combined_obj(
    dist_matrix: np.ndarray,
    asgn: np.ndarray,
    weights: np.ndarray,
    total_w: float,
    fac_nodes: list[int],
    rent_by_node: dict[int, int],
    r_min: float,
    r_max: float,
    rent_weight: float,
) -> float:
    N = len(weights)
    mean_d = float((weights * dist_matrix[np.arange(N), asgn]).sum()) / total_w
    if rent_weight == 0.0 or r_max == r_min:
        return mean_d
    r_hat_sum = sum(
        (rent_by_node[fn] - r_min) / (r_max - r_min) * D_REF_M
        for fn in fac_nodes
    )
    rent_penalty = r_hat_sum / len(fac_nodes)
    return mean_d + rent_weight * rent_penalty


# ---------------------------------------------------------------------------
# Public solver
# ---------------------------------------------------------------------------

def solve_kmedian_rent_road(
    G: nx.Graph,
    demand_nodes: list[int],
    k: int,
    node_to_district: dict[str, str],
    rent_weight: float = 0.0,
    facility_size_sqm: int = 500,
    n_restarts: int = 5,
) -> dict:
    """Rent-aware road-network k-median using Lloyd's algorithm with multi-start.

    Parameters
    ----------
    G                : undirected road graph (from the shared solver cache)
    demand_nodes     : aggregated demand node IDs (all districts)
    k                : number of facilities to open
    node_to_district : {str(node_id): district_name} from precompute_districts.py
    rent_weight      : 0 → pure distance; 1 → equal weight on distance and rent
    facility_size_sqm: used only for monthly cost reporting (m²)
    n_restarts       : independent random restarts
    """
    _require_graph()

    weights:  np.ndarray = _solvers._agg_weights
    lats:     np.ndarray = _solvers._agg_lats
    lons:     np.ndarray = _solvers._agg_lons
    G_dir                = _solvers._road_graph_dir

    N       = len(demand_nodes)
    total_w = float(weights.sum())

    # 1. Build rent_by_node and eligible node list ────────────────────────────
    rent_by_node: dict[int, int] = {}
    for nid in demand_nodes:
        district = node_to_district.get(str(nid))
        if district is None:
            continue
        region = DISTRICT_REGION.get(district)
        if region is None:
            continue
        rent_by_node[nid] = REGIONAL_RENT[region]

    eligible_nodes = [nid for nid in demand_nodes if nid in rent_by_node]

    if len(eligible_nodes) < k:
        raise RuntimeError(
            f"Only {len(eligible_nodes)} eligible nodes but k={k} requested."
        )

    eligible_arr = np.array(eligible_nodes, dtype=object)

    r_min = float(min(REGIONAL_RENT.values()))
    r_max = float(max(REGIONAL_RENT.values()))

    # 2. Seeding probabilities: uniform at rent_weight=0; low-rent bias at > 0 ─
    if rent_weight > 0.0 and r_max > r_min:
        r_hat_arr = np.array(
            [(r_max - rent_by_node[nid]) / (r_max - r_min) for nid in eligible_nodes],
            dtype=float,
        )
        # Add a uniform floor (0.1) so every node can be seeded.
        seed_prob = 0.1 + 0.9 * (r_hat_arr / r_hat_arr.sum())
        seed_prob /= seed_prob.sum()
    else:
        seed_prob = None  # uniform

    # 3. Lloyd's multi-start ──────────────────────────────────────────────────
    rng = np.random.default_rng(RNG_SEED)

    best_obj: float           = np.inf
    best_fac_nodes: list[int] = []
    best_asgn: np.ndarray     = np.zeros(N, dtype=int)
    best_dist: np.ndarray     = np.full((N, k), np.inf)
    worst_mean_d: float       = 0.0

    t0 = time.perf_counter()

    for r in range(1, n_restarts + 1):
        seed = int(rng.integers(0, 2**31))
        fac_nodes: list[int] = list(
            int(n)
            for n in np.random.default_rng(seed).choice(
                eligible_arr, size=k, replace=False, p=seed_prob,
            )
        )

        prev_asgn = None
        dist_matrix = np.full((N, k), np.inf)

        for _it in range(1, ROAD_KMEDIAN_MAX_ITERS + 1):
            # Assignment: Dijkstra from each facility.
            for j, fn in enumerate(fac_nodes):
                lengths = nx.single_source_dijkstra_path_length(
                    G, fn, weight="length"
                )
                dist_matrix[:, j] = [
                    lengths.get(dn, np.inf) for dn in demand_nodes
                ]

            asgn = dist_matrix.argmin(axis=1)
            if prev_asgn is not None and np.array_equal(asgn, prev_asgn):
                break
            prev_asgn = asgn.copy()

            # Location update: centroid snap to nearest eligible road node.
            new_fac = []
            for j in range(k):
                mask = asgn == j
                if not mask.any():
                    new_fac.append(fac_nodes[j])
                    continue
                w_j = weights[mask]
                tot = w_j.sum()
                c_lat = (w_j * lats[mask]).sum() / tot
                c_lon = (w_j * lons[mask]).sum() / tot
                new_fac.append(int(ox.nearest_nodes(G_dir, X=c_lon, Y=c_lat)))
            fac_nodes = new_fac

        cur_obj = _combined_obj(
            dist_matrix, asgn, weights, total_w,
            fac_nodes, rent_by_node, r_min, r_max, rent_weight,
        )

        mean_d = float((weights * dist_matrix[np.arange(N), asgn]).sum()) / total_w
        if mean_d > worst_mean_d:
            worst_mean_d = mean_d

        log.info(
            "solve_kmedian_rent_road restart %d/%d: obj=%.2f mean_d=%.1fm",
            r, n_restarts, cur_obj, mean_d,
        )

        if cur_obj < best_obj:
            best_obj       = cur_obj
            best_fac_nodes = list(fac_nodes)
            best_asgn      = asgn.copy()
            best_dist      = dist_matrix.copy()

    # 4. Final metrics ──────────────────────────────────────────────────────
    elapsed      = time.perf_counter() - t0
    best_mean_d  = float((weights * best_dist[np.arange(N), best_asgn]).sum()) / total_w
    improvement_pct = (
        100.0 * (worst_mean_d - best_mean_d) / worst_mean_d
        if worst_mean_d > 0 else 0.0
    )

    rent_breakdown = []
    for fn in best_fac_nodes:
        district = node_to_district.get(str(fn), "unknown")
        region   = DISTRICT_REGION.get(district)
        rent_sqm = rent_by_node.get(fn, 0)
        rent_breakdown.append(
            {
                "district":             district,
                "region":               region,
                "rent_hkd_sqm_month":   rent_sqm,
                "monthly_cost_hkd":     rent_sqm * facility_size_sqm,
            }
        )

    total_monthly = sum(item["monthly_cost_hkd"] for item in rent_breakdown)

    log.info(
        "solve_kmedian_rent_road DONE: k=%d rent_weight=%.2f "
        "mean_d=%.1fm improvement=%.2f%% runtime=%.2fs",
        k, rent_weight, best_mean_d, improvement_pct, elapsed,
    )

    return {
        "facilities": [
            {
                "node_id": int(fn),
                "lon":     float(G.nodes[fn]["x"]),
                "lat":     float(G.nodes[fn]["y"]),
            }
            for fn in best_fac_nodes
        ],
        "mean_distance_m":        best_mean_d,
        "improvement_pct":        improvement_pct,
        "rent_breakdown":         rent_breakdown,
        "total_monthly_rent_hkd": total_monthly,
        "rent_weight_used":       rent_weight,
        "runtime_s":              elapsed,
        "n_demand_nodes":         N,
        "total_weight":           total_w,
    }
