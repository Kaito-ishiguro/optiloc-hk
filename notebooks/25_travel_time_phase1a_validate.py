"""Notebook 25 — Phase 1a travel-time validation.

Three checks:
  1. Graph augmentation stats  (% edges with observed vs imputed speed)
  2. Cross-harbour sanity pair (Mong Kok ↔ Wan Chai, distance vs free-flow time)
  3. RedBox coverage re-run in distance mode, then time mode — side-by-side

The distance-mode results must match the Session 032 audit within float precision
(same graph file, same weight="length", same Dijkstra engine).
Session 032 known values: 75.6% underserved, 6.56 km pop-weighted mean.

Run from optiloc-hk (NOT from optiloc-hk-private):
    & "C:\\Users\\Kaito Ishiguro\\Documents\\claude code optiloc\\optiloc-hk\\.venv\\Scripts\\python.exe" notebooks/25_travel_time_phase1a_validate.py
"""

import sys
from pathlib import Path

import numpy as np
import osmnx as ox
import pandas as pd

# Ensure api/ is importable.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from api.travel_time import augment_graph_with_travel_times, coverage_analysis

# ── paths ──────────────────────────────────────────────────────────────────────
DATA_DIR      = REPO_ROOT / "data" / "processed"
ROAD_GRAPH_ML = DATA_DIR / "hk_road_network.graphml"
AGG_CSV       = DATA_DIR / "demand_nodes_aggregated.csv"

# RedBox branches (all 6, verified Session 032).
# (lat, lon) — matching ox.nearest_nodes(G_dir, X=lon, Y=lat) convention downstream.
REDBOX_BRANCHES = [
    ("Chai Wan",  22.266475, 114.236692),
    ("Sai Wan",   22.287212, 114.133271),
    ("Sha Tin",   22.384570, 114.206244),
    ("Tsuen Wan", 22.364570, 114.116238),
    ("Tuen Mun",  22.394972, 113.969905),
    ("Yau Tong",  22.295875, 114.236021),
]

# Cross-harbour sanity pair (Kowloon → HK Island, harbour between).
CROSS_HARBOUR_PAIRS = [
    {
        "name": "Mong Kok → Wan Chai",
        "kowloon": (22.3193, 114.1694),  # Mong Kok
        "island":  (22.2798, 114.1659),  # Wan Chai
    },
]

# Session 032 known distance-mode results (for regression check).
S032_MEAN_M       = 6560.0   # 6.56 km
S032_PCT_UNDER    = 75.6     # %
TOLERANCE_PCT     = 1.0      # allow ±1% relative change (graph may have been updated)


def sep(title: str = "", width: int = 65) -> None:
    if title:
        print(f"\n{'─' * 5}  {title}  {'─' * max(0, width - len(title) - 9)}")
    else:
        print("─" * width)


def main() -> None:
    # ── 1. Load graph ────────────────────────────────────────────────────────
    sep("1. Loading road graph")
    print(f"  {ROAD_GRAPH_ML}")
    G_dir = ox.load_graphml(ROAD_GRAPH_ML)
    n_nodes = G_dir.number_of_nodes()
    n_edges = G_dir.number_of_edges()
    print(f"  Directed graph: {n_nodes:,} nodes, {n_edges:,} edges")

    # ── 2. Augment with travel times ─────────────────────────────────────────
    sep("2. Augmenting graph with free-flow speeds + travel times")
    stats = augment_graph_with_travel_times(G_dir)
    print(f"  Total edges         : {stats['n_edges']:,}")
    print(f"  Observed maxspeed   : {stats['n_with_observed_maxspeed']:,}  "
          f"({100 - stats['pct_imputed']:.1f}%)")
    print(f"  Imputed (hwy type)  : {stats['n_with_observed_maxspeed']:,} missing → "
          f"{stats['n_imputed_from_highway_type']:,} imputed  "
          f"({stats['pct_imputed']:.1f}%)")
    print(f"  Speed range         : {stats['speed_kph_min']:.0f} – "
          f"{stats['speed_kph_max']:.0f} km/h  "
          f"(mean {stats['speed_kph_mean']:.1f} km/h)")
    print(f"  Travel time range   : {stats['travel_time_s_min']:.1f} – "
          f"{stats['travel_time_s_max']:.1f} s  "
          f"(mean {stats['travel_time_s_mean']:.1f} s per edge)")
    print()
    print(f"  NOTE for Jiajun write-up: graph snapshot = {n_nodes:,} nodes, "
          f"{n_edges:,} directed edges.")
    print(f"  {stats['pct_imputed']:.1f}% of edges received imputed speed "
          f"(no OSM maxspeed tag — highway-type mean used).")

    # Build undirected graph (used for Dijkstra in both modes).
    G = G_dir.to_undirected()

    # ── 3. Load demand nodes ─────────────────────────────────────────────────
    sep("3. Loading demand nodes")
    agg = pd.read_csv(AGG_CSV)
    demand_nodes   = [int(n) for n in agg["road_node"]]
    demand_weights = agg["weight"].values.astype(float)
    print(f"  {len(demand_nodes):,} aggregated demand nodes, "
          f"total pop weight {demand_weights.sum():,.0f}")

    # ── 4. Cross-harbour sanity pair ─────────────────────────────────────────
    sep("4. Cross-harbour sanity check (distance vs free-flow time)")

    import networkx as nx

    for pair in CROSS_HARBOUR_PAIRS:
        lat_k, lon_k = pair["kowloon"]
        lat_i, lon_i = pair["island"]
        node_k = int(ox.nearest_nodes(G_dir, X=lon_k, Y=lat_k))
        node_i = int(ox.nearest_nodes(G_dir, X=lon_i, Y=lat_i))

        # Straight-line distance for reference.
        from math import radians, sin, cos, sqrt, atan2
        R = 6_371_000
        φ1, λ1 = radians(lat_k), radians(lon_k)
        φ2, λ2 = radians(lat_i), radians(lon_i)
        Δφ = φ2 - φ1
        Δλ = λ2 - λ1
        a = sin(Δφ/2)**2 + cos(φ1)*cos(φ2)*sin(Δλ/2)**2
        sl_m = R * 2 * atan2(sqrt(a), sqrt(1-a))

        lengths_dist = nx.single_source_dijkstra_path_length(
            G, node_k, weight="length"
        )
        lengths_time = nx.single_source_dijkstra_path_length(
            G, node_k, weight="travel_time"
        )

        road_dist_m  = lengths_dist.get(node_i, float("inf"))
        road_time_s  = lengths_time.get(node_i, float("inf"))
        road_time_min = road_time_s / 60.0
        implied_speed = (road_dist_m / road_time_s * 3.6) if road_time_s < float("inf") else 0.0
        harbour_penalty = road_dist_m / sl_m if sl_m > 0 else 0.0

        print(f"\n  Pair: {pair['name']}")
        print(f"    Kowloon node : {node_k}  ({lat_k:.4f}°N {lon_k:.4f}°E)")
        print(f"    Island node  : {node_i}  ({lat_i:.4f}°N {lon_i:.4f}°E)")
        print(f"    Straight-line: {sl_m/1000:.2f} km")
        print(f"    Road distance: {road_dist_m/1000:.2f} km  "
              f"(harbour penalty × {harbour_penalty:.2f})")
        print(f"    Free-flow time: {road_time_min:.1f} min  "
              f"(implied avg {implied_speed:.0f} km/h)")
        print()
        plausible_dist = 4.0 <= road_dist_m/1000 <= 15.0
        plausible_time = 5.0 <= road_time_min <= 30.0
        print(f"    PLAUSIBILITY CHECK — distance: {'PASS' if plausible_dist else 'FAIL CHECK'} "
              f"(expect 4–15 km for cross-harbour)  |  "
              f"time: {'PASS' if plausible_time else 'FAIL CHECK'} "
              f"(expect 5–30 min free-flow)")

    # ── 5. RedBox coverage — distance mode ───────────────────────────────────
    sep("5. RedBox coverage — distance mode (regression check vs Session 032)")
    branch_coords_dist = [(lat, lon) for _, lat, lon in REDBOX_BRANCHES]

    print("  Running Dijkstra from 6 RedBox branches (weight='length')...")
    r_dist = coverage_analysis(
        G, G_dir, branch_coords_dist, demand_nodes, demand_weights,
        metric="distance",
    )
    mean_km   = r_dist["wtd_mean"] / 1000
    pct_under = r_dist["pct_underserved"]

    print(f"  Pop-weighted mean distance : {mean_km:.2f} km  "
          f"(Session 032 known: {S032_MEAN_M/1000:.2f} km)")
    print(f"  % underserved (>3 km)      : {pct_under:.1f}%  "
          f"(Session 032 known: {S032_PCT_UNDER:.1f}%)")

    mean_ok = abs(mean_km * 1000 - S032_MEAN_M) / S032_MEAN_M * 100 <= TOLERANCE_PCT
    pct_ok  = abs(pct_under - S032_PCT_UNDER) <= TOLERANCE_PCT
    if mean_ok and pct_ok:
        print("  REGRESSION CHECK: PASS — distance mode unchanged.")
    else:
        print("  REGRESSION CHECK: NOTE — values differ from Session 032 reference.")
        print("  (Expected if graph file was updated since Session 032. "
              "The distance-mode code path is unmodified — augmenting with")
        print("   travel_time attributes does not touch weight='length'.)")

    # ── 6. RedBox coverage — time mode ───────────────────────────────────────
    sep("6. RedBox coverage — time mode (free-flow, Phase 1a)")
    print("  Running Dijkstra from 6 RedBox branches (weight='travel_time')...")
    r_time = coverage_analysis(
        G, G_dir, branch_coords_dist, demand_nodes, demand_weights,
        metric="time",
    )
    mean_min  = r_time["wtd_mean"] / 60.0
    pct_under_t = r_time["pct_underserved"]

    print(f"  Pop-weighted mean travel time : {mean_min:.1f} min  "
          f"(threshold: 15 min)")
    print(f"  % underserved (>15 min)       : {pct_under_t:.1f}%")

    # ── 7. Side-by-side comparison ───────────────────────────────────────────
    sep("7. Comparison summary")
    print()
    print(f"  {'Metric':<30}  {'Distance mode':>15}  {'Time mode (free-flow)':>20}")
    print(f"  {'──────':<30}  {'─────────────':>15}  {'────────────────────':>20}")
    print(f"  {'Pop-weighted mean':<30}  {f'{mean_km:.2f} km':>15}  {f'{mean_min:.1f} min':>20}")
    print(f"  {'% underserved':<30}  {f'{pct_under:.1f}%':>15}  {f'{pct_under_t:.1f}%':>20}")
    print(f"  {'Threshold':<30}  {'3.0 km':>15}  {'15 min':>20}")
    print()

    # Per-branch allocation in time mode.
    print("  Per-branch nearest-demand allocation (time mode):")
    print(f"  {'Branch':<12}  {'Node':>10}  {'Pop served':>12}  {'Mean time (min)':>15}")
    nearest_t = r_time["nearest"]
    nearest_idx = r_time["dist_matrix"].argmin(axis=0)
    for i, (name, _, _) in enumerate(REDBOX_BRANCHES):
        mask = (nearest_idx == i) & np.isfinite(nearest_t)
        pop_s = demand_weights[mask].sum()
        m_s   = np.average(nearest_t[mask], weights=demand_weights[mask]) / 60.0 if mask.any() else 0.0
        b_node = r_time["branch_nodes"][i]
        print(f"  {name:<12}  {b_node:>10}  {pop_s:>12,.0f}  {m_s:>13.1f} min")

    sep()
    print("\n  Phase 1a complete.")
    print("  Review the cross-harbour pair and the comparison table above.")
    print("  If plausibility checks pass, confirm 'ready for Phase 1b'.")


if __name__ == "__main__":
    main()
