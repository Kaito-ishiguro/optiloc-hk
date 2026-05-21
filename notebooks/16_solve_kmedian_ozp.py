"""
notebooks/16_solve_kmedian_ozp.py

Session 012: k-median network optimization with OZP commercial constraint.

Combines Session 011's Lloyd's algorithm outer loop with Session 010b's
constrained Weber sub-solver (SLSQP + buffered OZP commercial union).

Inner-solver strategy is conditional invocation:
  1. Run unconstrained Weiszfeld on the cluster.
  2. If the result lies inside the OZP commercial union, keep it.
  3. Else, fall back to SLSQP warm-started from the Weiszfeld result.

This isolates the expensive constrained solve to clusters whose unconstrained
Weber center falls outside commercial land (mostly NT clusters), keeping
runtime tractable across 10 restarts x ~15 Lloyd iters x 5 facilities.
"""

import time
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from scipy.optimize import minimize

# ---------- Constants (matched to Session 011 for direct comparability) ----------
K = 5
N_RESTARTS = 10
MAX_LLOYD_ITERS = 50
WEISZFELD_TOL = 1e-7
WEISZFELD_MAX_ITER = 100
EPS = 1e-9
BUFFER = 1e-6           # Session 010b smoothness fix (~10 cm on the ground)
SLSQP_MAXITER = 200
SLSQP_FTOL = 1e-8
RNG_SEED = 42

DATA_DIR = Path("data/processed")
DEMAND_CSV = DATA_DIR / "demand_points.csv"
OZP_GEOJSON = DATA_DIR / "ozp_commercial_union.geojson"
OUT_RESULT = DATA_DIR / "kmedian_ozp_result.csv"
OUT_TRAILS = DATA_DIR / "kmedian_ozp_trails.csv"
OUT_DIAG = DATA_DIR / "kmedian_ozp_diagnostics.csv"


# ---------- Inner solvers ----------
def weighted_objective(x, demand, weights):
    """Total weighted Euclidean distance from x to (demand, weights)."""
    diff = demand - x
    d = np.sqrt(np.sum(diff * diff, axis=1) + EPS)
    return float(np.sum(weights * d))


def weiszfeld(demand, weights, x_init, tol=WEISZFELD_TOL, max_iter=WEISZFELD_MAX_ITER):
    """
    Unconstrained Weber via the FONC fixed-point iteration:
        x_{k+1} = sum_i (w_i / d_i^k) x_i  /  sum_i (w_i / d_i^k)
    Returns (x_final, n_iters).
    """
    x = np.asarray(x_init, dtype=float).copy()
    for it in range(1, max_iter + 1):
        diff = demand - x
        d = np.sqrt(np.sum(diff * diff, axis=1) + EPS)
        u = weights / d
        x_new = (u[:, None] * demand).sum(axis=0) / u.sum()
        if np.linalg.norm(x_new - x) < tol:
            return x_new, it
        x = x_new
    return x, max_iter


def slsqp_constrained(demand, weights, x_init, feasible_geom):
    """
    Constrained Weber via SLSQP. Constraint: signed distance to feasible_geom >= 0
    (SLSQP 'ineq' convention is fun(x) >= 0 = feasible).
    feasible_geom must be pre-buffered by the caller.
    Returns (x_final, n_iters, success_flag).
    """
    def obj(x):
        return weighted_objective(x, demand, weights)

    def signed_distance(x):
        pt = Point(x[0], x[1])
        if feasible_geom.contains(pt):
            return pt.distance(feasible_geom.boundary)
        return -pt.distance(feasible_geom)

    cons = [{"type": "ineq", "fun": signed_distance}]
    result = minimize(
        obj,
        x_init,
        method="SLSQP",
        constraints=cons,
        options={"maxiter": SLSQP_MAXITER, "ftol": SLSQP_FTOL, "disp": False},
    )
    return result.x, int(result.nit), bool(result.success)


def constrained_weber_update(demand, weights, x_init, feasible_geom):
    """
    Per-cluster Weber sub-solve with conditional SLSQP invocation.
    Returns (x_final, used_slsqp, weiszfeld_iters, slsqp_iters_or_None).
    """
    x_uncon, w_iters = weiszfeld(demand, weights, x_init)
    if feasible_geom.contains(Point(x_uncon[0], x_uncon[1])):
        return x_uncon, False, w_iters, None
    x_con, s_iters, _ = slsqp_constrained(demand, weights, x_uncon, feasible_geom)
    return x_con, True, w_iters, s_iters


# ---------- Outer Lloyd loop ----------
def assign_demand(demand, facilities):
    """a[i] = argmin_j ||demand[i] - facilities[j]||."""
    diff = demand[:, None, :] - facilities[None, :, :]     # (n, k, 2)
    d2 = np.sum(diff * diff, axis=2)                       # (n, k)
    return np.argmin(d2, axis=1)


def total_weighted_objective(demand, weights, facilities, assignment):
    """Total k-median objective: sum_i w_i ||x_i - F_{a_i}||."""
    chosen = facilities[assignment]
    d = np.sqrt(np.sum((demand - chosen) ** 2, axis=1))
    return float(np.sum(weights * d))


def lloyd_one_restart(demand, weights, feasible_geom, k, rng, restart_id):
    """One full Lloyd run from a weighted-random init. Returns a results dict."""
    n = len(demand)
    probs = weights / weights.sum()
    init_idx = rng.choice(n, size=k, replace=False, p=probs)
    facilities = demand[init_idx].copy()

    trail = [facilities.copy()]
    prev_assignment = None
    slsqp_calls = 0
    weiszfeld_calls = 0
    converged = False

    for it in range(1, MAX_LLOYD_ITERS + 1):
        assignment = assign_demand(demand, facilities)

        if prev_assignment is not None and np.array_equal(assignment, prev_assignment):
            converged = True
            break

        new_facilities = facilities.copy()
        for j in range(k):
            mask = assignment == j
            if not mask.any():
                continue  # empty cluster: leave facility in place
            x_new, used_slsqp, _, _ = constrained_weber_update(
                demand[mask], weights[mask], facilities[j], feasible_geom
            )
            new_facilities[j] = x_new
            weiszfeld_calls += 1
            if used_slsqp:
                slsqp_calls += 1

        facilities = new_facilities
        trail.append(facilities.copy())
        prev_assignment = assignment

    # Final consistent assignment + objective with the final facility positions
    final_assignment = assign_demand(demand, facilities)
    final_obj = total_weighted_objective(demand, weights, facilities, final_assignment)

    return {
        "restart_id": restart_id,
        "facilities": facilities,
        "trail": trail,
        "final_obj": final_obj,
        "n_lloyd_iters": it,
        "converged": converged,
        "slsqp_calls": slsqp_calls,
        "weiszfeld_calls": weiszfeld_calls,
    }


# ---------- Main ----------
def main():
    print("=" * 64)
    print("Session 012: k-median + OZP commercial constraint")
    print("=" * 64)

    print(f"\nLoading demand points from {DEMAND_CSV} ...")
    df_dem = pd.read_csv(DEMAND_CSV)
    demand = df_dem[["lon", "lat"]].to_numpy(dtype=float)
    weights = df_dem["weight"].to_numpy(dtype=float)
    print(f"  {len(demand):,} demand points, total weight {weights.sum():,.0f}")

    print(f"\nLoading OZP commercial union from {OZP_GEOJSON} ...")
    ozp_gdf = gpd.read_file(OZP_GEOJSON)
    raw_geom = ozp_gdf.iloc[0].geometry
    feasible_geom = raw_geom.buffer(BUFFER)
    n_pieces = len(feasible_geom.geoms) if hasattr(feasible_geom, "geoms") else 1
    print(f"  Geometry type: {feasible_geom.geom_type}  ({n_pieces} pieces)")
    print(f"  Buffered by {BUFFER} deg (~10 cm) per Session 010b")

    print(f"\nRunning {N_RESTARTS} weighted-random restarts (K={K}) ...")
    rng = np.random.default_rng(RNG_SEED)
    t0 = time.time()
    results = []
    for r in range(1, N_RESTARTS + 1):
        rt0 = time.time()
        res = lloyd_one_restart(demand, weights, feasible_geom, K, rng, r)
        res["runtime_s"] = time.time() - rt0
        results.append(res)
        print(
            f"  Restart {r:2d}: obj={res['final_obj']:>10,.0f}  "
            f"iters={res['n_lloyd_iters']:>2d}  "
            f"SLSQP={res['slsqp_calls']:>3d}/{res['weiszfeld_calls']:>3d}  "
            f"converged={str(res['converged']):>5s}  "
            f"t={res['runtime_s']:.2f}s"
        )
    total_t = time.time() - t0
    print(f"\nTotal multi-start runtime: {total_t:.2f}s")

    best = min(results, key=lambda r: r["final_obj"])
    best_obj = best["final_obj"]
    worst_obj = max(r["final_obj"] for r in results)
    gap_pct = 100.0 * (worst_obj - best_obj) / best_obj
    distinct_objs = sorted({round(r["final_obj"], 0) for r in results})
    print(f"\nBest objective (restart {best['restart_id']}): {best_obj:,.0f}")
    print(f"Worst objective:                            {worst_obj:,.0f}")
    print(f"Worst-best gap:                             {gap_pct:.1f}%")
    print(f"Distinct local optima (rounded):            {len(distinct_objs)}")

    print("\nReduction vs baselines:")
    print(f"  Single-facility Weber (Session 003):  671,466")
    print(f"  k=5 unconstrained (Session 011):      274,830")
    print(f"  k=5 OZP-constrained (Session 012):    {best_obj:>10,.0f}")
    pct_vs_uncon = 100.0 * (best_obj - 274_830) / 274_830
    print(f"  Penalty from OZP constraint:          {pct_vs_uncon:+.1f}%")

    print("\nWinning restart - final 5 facility locations:")
    for j, (lon, lat) in enumerate(best["facilities"]):
        print(f"  F{j+1}: ({lon:.5f}, {lat:.5f})")

    print("\nWriting outputs ...")
    pd.DataFrame({
        "facility_id": range(K),
        "lon": best["facilities"][:, 0],
        "lat": best["facilities"][:, 1],
    }).to_csv(OUT_RESULT, index=False)
    print(f"  {OUT_RESULT}")

    trail_rows = []
    for snap_iter, snap in enumerate(best["trail"]):
        for j in range(K):
            trail_rows.append({
                "iter": snap_iter,
                "facility_id": j,
                "lon": snap[j, 0],
                "lat": snap[j, 1],
            })
    pd.DataFrame(trail_rows).to_csv(OUT_TRAILS, index=False)
    print(f"  {OUT_TRAILS}")

    diag_rows = [
        {
            "restart_id": r["restart_id"],
            "n_lloyd_iters": r["n_lloyd_iters"],
            "converged": r["converged"],
            "slsqp_calls": r["slsqp_calls"],
            "weiszfeld_calls": r["weiszfeld_calls"],
            "final_obj": r["final_obj"],
            "runtime_s": r["runtime_s"],
        }
        for r in results
    ]
    pd.DataFrame(diag_rows).to_csv(OUT_DIAG, index=False)
    print(f"  {OUT_DIAG}")

    print("\nDone.")


if __name__ == "__main__":
    main()
