"""
14_solve_kmedian.py — Multi-facility k-median with Lloyd's algorithm
and Weiszfeld inner solver.

Problem: place k facilities {F_1, ..., F_k} in HK to minimize
    sum_i w_i * ||x_i - F_{a_i}||
where a_i in {1, ..., k} assigns demand point i to its nearest facility.

Method:
  Lloyd's algorithm (alternating optimization):
    1. assignment step:  a_i = argmin_j ||x_i - F_j||
    2. update step:      F_j = Weber center of its cluster (via Weiszfeld)
    repeat until assignments unchanged.
  Multi-start with N_RESTARTS random inits, keep the best objective.
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data" / "processed"

# --- hyperparameters ---
K = 5
N_RESTARTS = 10
MAX_LLOYD_ITERS = 50
WEISZFELD_TOL = 1e-7
WEISZFELD_MAX_ITERS = 100
EPS = 1e-9
RNG_SEED = 42

# --- load demand points ---
print(f"Loading demand points from demand_points.csv ...")
df = pd.read_csv(DATA / "demand_points.csv")
points = df[["lon", "lat"]].values          # shape (n, 2)
weights = df["weight"].values.astype(float) # shape (n,)
n = len(points)
print(f"  {n:,} demand points, total weight {weights.sum():,.0f}")
print(f"  k={K}, restarts={N_RESTARTS}, max_lloyd_iters={MAX_LLOYD_ITERS}")


# --- Weiszfeld inner solver (Session 008) ---
def weiszfeld(cluster_points, cluster_weights, x0):
    """Solve the Weber problem on one cluster. Returns (x*, iters)."""
    x = x0.copy()
    for it in range(WEISZFELD_MAX_ITERS):
        diffs = cluster_points - x                              # (m, 2)
        d = np.sqrt((diffs ** 2).sum(axis=1) + EPS)             # (m,)
        u = cluster_weights / d                                 # (m,)
        x_new = (u[:, None] * cluster_points).sum(axis=0) / u.sum()
        if np.linalg.norm(x_new - x) < WEISZFELD_TOL:
            return x_new, it + 1
        x = x_new
    return x, WEISZFELD_MAX_ITERS


# --- total objective (sum of weighted distances to nearest facility) ---
def objective(facilities, points, weights):
    # distances: (n, k)
    dists = np.sqrt(((points[:, None, :] - facilities[None, :, :]) ** 2).sum(axis=2))
    min_dists = dists.min(axis=1)
    return float((weights * min_dists).sum())


# --- one Lloyd run from a given init ---
def lloyd_run(facilities_init, points, weights):
    facilities = facilities_init.copy()
    trail = [facilities.copy()]
    prev_assignments = None
    for lloyd_iter in range(MAX_LLOYD_ITERS):
        # assignment step
        dists = np.sqrt(((points[:, None, :] - facilities[None, :, :]) ** 2).sum(axis=2))
        assignments = dists.argmin(axis=1)

        # convergence check: assignments unchanged from previous iter
        if prev_assignments is not None and np.array_equal(assignments, prev_assignments):
            return facilities, trail, lloyd_iter, "converged"
        prev_assignments = assignments

        # update step: Weiszfeld per cluster
        new_facilities = facilities.copy()
        for j in range(K):
            mask = assignments == j
            if not mask.any():
                continue  # stranded facility, leave it in place
            new_facilities[j], _ = weiszfeld(points[mask], weights[mask], facilities[j])
        facilities = new_facilities
        trail.append(facilities.copy())

    return facilities, trail, MAX_LLOYD_ITERS, "max_iters"


# --- weighted-random init: sample k demand points proportional to weight ---
def weighted_init(rng):
    probs = weights / weights.sum()
    idx = rng.choice(n, size=K, replace=False, p=probs)
    return points[idx].copy()


# --- multi-start ---
rng = np.random.default_rng(RNG_SEED)
best_obj = np.inf
best_facilities = None
best_trail = None
best_iters = None
best_status = None
best_restart = None

print(f"\nRunning {N_RESTARTS} restarts ...")
t0 = time.time()
for restart in range(N_RESTARTS):
    init = weighted_init(rng)
    facilities, trail, iters, status = lloyd_run(init, points, weights)
    obj = objective(facilities, points, weights)
    marker = ""
    if obj < best_obj:
        best_obj = obj
        best_facilities = facilities
        best_trail = trail
        best_iters = iters
        best_status = status
        best_restart = restart
        marker = "  <-- new best"
    print(f"  restart {restart+1:2d}: obj={obj:>13,.1f}  iters={iters:>2d}  {status}{marker}")
elapsed = time.time() - t0

print(f"\nBest restart: #{best_restart + 1}")
print(f"  Objective:           {best_obj:,.1f}")
print(f"  Lloyd iterations:    {best_iters}  ({best_status})")
print(f"  Total time:          {elapsed:.2f}s")
print(f"  Single-facility ref: 671,466.7  (Session 003)")
print(f"  Reduction:           {(1 - best_obj/671466.7)*100:.1f}%")

print(f"\nFinal k={K} facility locations:")
for j in range(K):
    print(f"  F{j+1}: lon={best_facilities[j, 0]:.5f}, lat={best_facilities[j, 1]:.5f}")

# --- save ---
result_df = pd.DataFrame({
    "facility_id": range(K),
    "lon": best_facilities[:, 0],
    "lat": best_facilities[:, 1],
})
result_df.to_csv(DATA / "kmedian_result.csv", index=False)

trail_rows = []
for it, facs in enumerate(best_trail):
    for j in range(K):
        trail_rows.append({
            "iter": it,
            "facility_id": j,
            "lon": facs[j, 0],
            "lat": facs[j, 1],
        })
trail_df = pd.DataFrame(trail_rows)
trail_df.to_csv(DATA / "kmedian_trails.csv", index=False)

print(f"\nSaved kmedian_result.csv ({len(result_df)} rows)")
print(f"Saved kmedian_trails.csv ({len(trail_df)} rows)")