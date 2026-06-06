"""Rent-aware k-median solver for OptiLoc HK.

Minimises a combined objective:

    obj = mean_coverage_m + rent_weight * rent_penalty_m

where:
    mean_coverage_m  = Σ(w_i × d_i) / Σ(w_i)          (pop-weighted mean road distance)
    rent_penalty_m   = mean(r̂_j for j in facilities)   (mean normalised rent, in metres)
    r̂_j             = (rent_j − r_min) / (r_max − r_min) × D_REF_M

At rent_weight=0 the objective reduces to the standard k-median distance objective,
giving the same result as solve_kmedian_road.

Algorithm: greedy interchange local search with multi-restart (Maranzana-style),
identical in structure to api/mclp.py — only the objective function changes.

Facility candidates are restricted to nodes whose district has industrial-rental
data (excludes Wan Chai, Sha Tin, Islands — zero industrial stock or vacancy).
Demand nodes are unchanged: all 18k+ aggregated demand nodes contribute to the
mean-distance objective regardless of district.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import networkx as nx
import numpy as np

import api.solvers as _solvers
from api.config import RNG_SEED
from api.rent_data import D_REF_M, DISTRICT_REGION, REGIONAL_RENT

log = logging.getLogger(__name__)

# Interchange iteration cap.
_MAX_ITERS: int = 50

# Maximum candidate nodes tried per facility per interchange pass.
# Ranked by demand weight — highest-weight eligible nodes are the best swap
# targets for a distance-minimising objective.
_MAX_CANDIDATES: int = 200


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require_graph() -> None:
    if _solvers._road_graph is None or _solvers._agg_demand_nodes is None:
        raise RuntimeError(
            "Road graph not initialised — initialize_solvers() must be called "
            "before solve_kmedian_rent_road()."
        )


def _dist_col(node: int, demand_nodes: list[int]) -> np.ndarray:
    """Road distances (metres) from *node* to every aggregated demand node."""
    lengths = dict(
        nx.single_source_dijkstra_path_length(
            _solvers._road_graph, node, weight="length"
        )
    )
    return np.array([lengths.get(dn, np.inf) for dn in demand_nodes], dtype=float)


def _combined_obj(
    nearest: np.ndarray,
    weights: np.ndarray,
    total_w: float,
    fac_nodes: list[int],
    rent_by_node: dict[int, int],
    r_min: float,
    r_max: float,
    rent_weight: float,
) -> float:
    """Combined objective: mean distance + normalised rent penalty (both in metres)."""
    mean_d = float((weights * nearest).sum()) / total_w
    if rent_weight == 0.0 or r_max == r_min:
        return mean_d
    r_hat_sum = sum(
        (rent_by_node[fn] - r_min) / (r_max - r_min) * D_REF_M
        for fn in fac_nodes
    )
    rent_penalty = r_hat_sum / len(fac_nodes)
    return mean_d + rent_weight * rent_penalty


def _rent_penalty_excl(
    fac_nodes: list[int],
    exclude_idx: int,
    rent_by_node: dict[int, int],
    r_min: float,
    r_max: float,
) -> float:
    """Sum of r̂_j for all facilities except the one at exclude_idx."""
    total = 0.0
    for i, fn in enumerate(fac_nodes):
        if i != exclude_idx:
            total += (rent_by_node[fn] - r_min) / (r_max - r_min) * D_REF_M
    return total


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
    """Rent-aware road-network k-median.

    Parameters
    ----------
    G                : undirected road graph (from the shared solver cache)
    demand_nodes     : aggregated demand node IDs (all districts)
    k                : number of facilities to open
    node_to_district : {str(node_id): district_name} from precompute_districts.py
    rent_weight      : 0 → pure distance; 1 → equal weight on distance and rent
    facility_size_sqm: used only for monthly cost reporting (m²)
    n_restarts       : independent random restarts

    Returns
    -------
    dict matching SolveKmedianRentResponse
    """
    _require_graph()

    weights: np.ndarray = _solvers._agg_weights
    G_dir               = _solvers._road_graph_dir

    N       = len(demand_nodes)
    total_w = float(weights.sum())

    # 1. Build rent_by_node: node_id → HK$/sqm/month (eligible nodes only) ──
    rent_by_node: dict[int, int] = {}
    for nid in demand_nodes:
        district = node_to_district.get(str(nid))
        if district is None:
            continue
        region = DISTRICT_REGION.get(district)
        if region is None:
            continue  # excluded district
        rent_by_node[nid] = REGIONAL_RENT[region]

    eligible_nodes = [nid for nid in demand_nodes if nid in rent_by_node]

    if len(eligible_nodes) < k:
        raise RuntimeError(
            f"Only {len(eligible_nodes)} eligible nodes (non-excluded districts) "
            f"but k={k} facilities requested."
        )

    # Normalisation bounds.
    r_min = float(min(REGIONAL_RENT.values()))   # 164
    r_max = float(max(REGIONAL_RENT.values()))   # 218

    # 2. Pre-ranked candidate list for interchange (top by demand weight) ────
    eligible_set   = set(eligible_nodes)
    eligible_idx   = [i for i, dn in enumerate(demand_nodes) if dn in eligible_set]
    eligible_w     = weights[eligible_idx]
    top_order      = np.argsort(eligible_w)[::-1][:_MAX_CANDIDATES]
    top_candidates = [demand_nodes[eligible_idx[i]] for i in top_order]

    # 3. Multi-restart interchange search ─────────────────────────────────
    rng = np.random.default_rng(RNG_SEED)

    best_obj: float             = np.inf
    best_fac_nodes: list[int]   = []
    best_nearest: np.ndarray    = np.full(N, np.inf)
    worst_mean_d: float         = 0.0

    t0 = time.perf_counter()

    for restart in range(1, n_restarts + 1):

        # Seed k facility nodes from eligible nodes.
        seed = int(rng.integers(0, 2**31))
        fac_nodes: list[int] = list(
            int(n)
            for n in np.random.default_rng(seed).choice(
                eligible_nodes, size=k, replace=False
            )
        )

        # Build initial distance matrix (N × k).
        dist = np.column_stack(
            [_dist_col(fn, demand_nodes) for fn in fac_nodes]
        )  # (N, k)

        nearest  = dist.min(axis=1)
        cur_obj  = _combined_obj(
            nearest, weights, total_w, fac_nodes,
            rent_by_node, r_min, r_max, rent_weight,
        )

        # Greedy interchange loop.
        improved = True
        n_iters  = 0

        while improved and n_iters < _MAX_ITERS:
            improved = False
            n_iters += 1
            fac_set  = set(fac_nodes)

            for j in range(k):
                # Nearest distance excluding facility j.
                if k == 1:
                    nearest_excl_j = np.full(N, np.inf)
                else:
                    mask           = np.ones(k, dtype=bool)
                    mask[j]        = False
                    nearest_excl_j = dist[:, mask].min(axis=1)

                # Rent contribution of all facilities except j.
                rent_excl_j = _rent_penalty_excl(
                    fac_nodes, j, rent_by_node, r_min, r_max
                )

                candidates = [c for c in top_candidates if c not in fac_set]

                log.debug(
                    "  restart %d iter %d fac %d: trying %d candidates",
                    restart, n_iters, j, len(candidates),
                )

                for cand in candidates:
                    d_cand      = _dist_col(cand, demand_nodes)
                    new_nearest = np.minimum(nearest_excl_j, d_cand)

                    new_mean_d = float((weights * new_nearest).sum()) / total_w
                    if rent_weight == 0.0 or r_max == r_min:
                        new_obj = new_mean_d
                    else:
                        r_hat_cand  = (rent_by_node[cand] - r_min) / (r_max - r_min) * D_REF_M
                        new_rent    = (rent_excl_j + r_hat_cand) / k
                        new_obj     = new_mean_d + rent_weight * new_rent

                    if new_obj < cur_obj - 1e-6:
                        fac_nodes[j]  = cand
                        dist[:, j]    = d_cand
                        nearest       = new_nearest
                        cur_obj       = new_obj
                        fac_set       = set(fac_nodes)
                        improved      = True
                        break  # restart facility loop

                if improved:
                    break

        log.info(
            "solve_kmedian_rent_road restart %d/%d: obj=%.2f iters=%d",
            restart, n_restarts, cur_obj, n_iters,
        )

        mean_d = float((weights * nearest).sum()) / total_w
        if mean_d > worst_mean_d:
            worst_mean_d = mean_d

        if cur_obj < best_obj:
            best_obj       = cur_obj
            best_fac_nodes = list(fac_nodes)
            best_nearest   = nearest.copy()

    # 4. Final metrics ──────────────────────────────────────────────────────
    elapsed      = time.perf_counter() - t0
    best_mean_d  = float((weights * best_nearest).sum()) / total_w
    improvement_pct = (
        100.0 * (worst_mean_d - best_mean_d) / worst_mean_d
        if worst_mean_d > 0 else 0.0
    )

    # Rent breakdown (one entry per facility).
    rent_breakdown = []
    for fn in best_fac_nodes:
        district = node_to_district.get(str(fn), "unknown")
        region   = DISTRICT_REGION.get(district)
        rent_sqm = rent_by_node.get(fn, 0)
        monthly  = rent_sqm * facility_size_sqm
        rent_breakdown.append(
            {
                "district":         district,
                "region":           region,
                "rent_hkd_sqm_month": rent_sqm,
                "monthly_cost_hkd": monthly,
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
        "mean_distance_m":       best_mean_d,
        "improvement_pct":       improvement_pct,
        "rent_breakdown":        rent_breakdown,
        "total_monthly_rent_hkd": total_monthly,
        "rent_weight_used":      rent_weight,
        "runtime_s":             elapsed,
        "n_demand_nodes":        N,
        "total_weight":          total_w,
    }
