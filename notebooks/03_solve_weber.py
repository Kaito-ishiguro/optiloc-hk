"""
OptiLoc HK — Session 003: Weber problem solver

Solves the weighted facility location problem
    min  f(x, y) = sum_i w_i * sqrt((x - x_i)^2 + (y - y_i)^2)
on the 41,288 demand points produced by Session 002, using:

  1. Gradient descent       (first-order method, hand-rolled)
  2. Newton-Raphson         (second-order method, hand-rolled)
  3. SciPy BFGS             (reference baseline for sanity check)

Saves iteration trails for both hand-rolled methods so the next session
can animate them on a Folium map.

Run from repo root:
    python notebooks/03_solve_weber.py
"""

from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.optimize import minimize

# =============================================================================
# Paths
# =============================================================================
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
INPUT_CSV = DATA_PROCESSED / "demand_points.csv"
TRAIL_GD_CSV = DATA_PROCESSED / "trail_gradient_descent.csv"
TRAIL_NEWTON_CSV = DATA_PROCESSED / "trail_newton.csv"
RESULTS_CSV = DATA_PROCESSED / "solver_results.csv"

EPS = 1e-9        # added to d_i to avoid division by zero at demand points
GRAD_TOL = 1e-3   # convergence tolerance on ||grad f||

# =============================================================================
# Step 1 — Load demand points
# =============================================================================
df = pd.read_csv(INPUT_CSV)
xs = df["lon"].to_numpy()        # x_i — longitudes
ys = df["lat"].to_numpy()        # y_i — latitudes
ws = df["weight"].to_numpy()     # w_i — populations
n = len(df)
print(f"Loaded {n:,} demand points (total weight: {ws.sum():,.0f})")

# Starting point: centroid of HK (roughly Victoria Harbour).
# Convex objective => any starting point converges to the same global minimum,
# so we pick something reasonable just to make convergence visualisations clean.
START = np.array([114.17, 22.32])


# =============================================================================
# Step 2 — Objective, gradient, Hessian (vectorized NumPy)
#
# We never write a Python loop over the 41,288 demand points. Instead, every
# operation is an array op acting on all points simultaneously. This is what
# makes 41k points feasible — a Python loop would take ~30 seconds per
# function call; vectorized NumPy takes ~1 millisecond.
# =============================================================================

def objective(p):
    """f(x, y) = sum_i w_i * d_i"""
    dx = p[0] - xs
    dy = p[1] - ys
    d = np.sqrt(dx**2 + dy**2 + EPS)
    return float(np.sum(ws * d))


def gradient(p):
    """grad f = sum_i (w_i / d_i) * (x - x_i, y - y_i)"""
    dx = p[0] - xs
    dy = p[1] - ys
    d = np.sqrt(dx**2 + dy**2 + EPS)
    coef = ws / d                       # shape (n,)
    g = np.array([
        np.sum(coef * dx),
        np.sum(coef * dy),
    ])
    return g


def hessian(p):
    """
    H = sum_i (w_i / d_i^3) * [[(y-y_i)^2,           -(x-x_i)(y-y_i)],
                               [-(x-x_i)(y-y_i),     (x-x_i)^2       ]]
    """
    dx = p[0] - xs
    dy = p[1] - ys
    d = np.sqrt(dx**2 + dy**2 + EPS)
    coef = ws / (d**3)                  # shape (n,)
    H_xx = np.sum(coef * dy**2)
    H_yy = np.sum(coef * dx**2)
    H_xy = -np.sum(coef * dx * dy)
    return np.array([[H_xx, H_xy], [H_xy, H_yy]])


# =============================================================================
# Step 3 — Gradient descent (from scratch)
#
# Update rule:   x_{k+1} = x_k - alpha * grad f(x_k)
#
# We use a small constant step size. Note that the gradient magnitude scales
# with total population (~7.5M), so a sensible step size is small.
# =============================================================================

def gradient_descent(start, alpha=1e-9, max_iter=10_000, tol=GRAD_TOL):
    p = np.array(start, dtype=float)
    trail = [p.copy()]
    t0 = time.perf_counter()
    for k in range(1, max_iter + 1):
        g = gradient(p)
        gnorm = np.linalg.norm(g)
        if gnorm < tol:
            break
        p = p - alpha * g
        trail.append(p.copy())
    elapsed = time.perf_counter() - t0
    return {
        "method": "Gradient Descent",
        "x_opt": p,
        "f_opt": objective(p),
        "iterations": k,
        "grad_norm": float(np.linalg.norm(gradient(p))),
        "elapsed_sec": elapsed,
        "trail": np.array(trail),
    }


# =============================================================================
# Step 4 — Newton-Raphson (from scratch)
#
# Update rule:   solve H * p = -grad f, then x_{k+1} = x_k + p
#
# We solve the linear system rather than computing H^{-1}. For 2x2 the
# saving is negligible, but it's the correct habit at scale and avoids
# the numerical instability of explicit matrix inversion.
# =============================================================================

def newton_raphson(start, max_iter=100, tol=GRAD_TOL):
    p = np.array(start, dtype=float)
    trail = [p.copy()]
    t0 = time.perf_counter()
    for k in range(1, max_iter + 1):
        g = gradient(p)
        gnorm = np.linalg.norm(g)
        if gnorm < tol:
            break
        H = hessian(p)
        step = np.linalg.solve(H, -g)   # solve H * step = -g
        p = p + step
        trail.append(p.copy())
    elapsed = time.perf_counter() - t0
    return {
        "method": "Newton-Raphson",
        "x_opt": p,
        "f_opt": objective(p),
        "iterations": k,
        "grad_norm": float(np.linalg.norm(gradient(p))),
        "elapsed_sec": elapsed,
        "trail": np.array(trail),
    }


# =============================================================================
# Step 5 — SciPy BFGS sanity check
#
# Quasi-Newton method: approximates the Hessian from gradient history.
# If our hand-rolled solvers disagree with SciPy, we have a bug.
# =============================================================================

def scipy_bfgs(start):
    t0 = time.perf_counter()
    res = minimize(
        objective,
        x0=np.array(start, dtype=float),
        jac=gradient,
        method="BFGS",
        options={"gtol": GRAD_TOL},
    )
    elapsed = time.perf_counter() - t0
    return {
        "method": "SciPy BFGS",
        "x_opt": res.x,
        "f_opt": float(res.fun),
        "iterations": int(res.nit),
        "grad_norm": float(np.linalg.norm(res.jac)),
        "elapsed_sec": elapsed,
        "trail": None,
    }


# =============================================================================
# Step 6 — Run all three solvers
# =============================================================================
print(f"\nStarting point: ({START[0]:.4f}, {START[1]:.4f})")
print(f"Convergence tolerance: ||grad f|| < {GRAD_TOL}\n")

results = [
    gradient_descent(START),
    newton_raphson(START),
    scipy_bfgs(START),
]


# =============================================================================
# Step 7 — Print comparison table
# =============================================================================
print("=" * 78)
print(f"{'Method':<20} {'Iters':>8} {'lon':>10} {'lat':>10} "
      f"{'f(x*)':>14} {'time (s)':>10}")
print("-" * 78)
for r in results:
    print(f"{r['method']:<20} {r['iterations']:>8} "
          f"{r['x_opt'][0]:>10.5f} {r['x_opt'][1]:>10.5f} "
          f"{r['f_opt']:>14,.2f} {r['elapsed_sec']:>10.4f}")
print("=" * 78)

# Cross-method consistency check — if the three optima differ noticeably,
# something is wrong (most likely a bug in the gradient or Hessian).
opts = np.array([r["x_opt"] for r in results])
spread = float(np.max(np.linalg.norm(opts - opts.mean(axis=0), axis=1)))
print(f"\nMax distance between any two optima: {spread:.6f} degrees "
      f"(~{spread * 111_000:.1f} m on the ground)")
if spread > 1e-3:
    print("WARNING: solvers disagree by more than 100m. Check derivations.")
else:
    print("Solvers agree. Hand-rolled gradient and Hessian are consistent with SciPy.")


# =============================================================================
# Step 8 — Save iteration trails for the next visualization session
# =============================================================================
gd_trail_df = pd.DataFrame(results[0]["trail"], columns=["lon", "lat"])
gd_trail_df["iter"] = np.arange(len(gd_trail_df))
gd_trail_df.to_csv(TRAIL_GD_CSV, index=False)

nr_trail_df = pd.DataFrame(results[1]["trail"], columns=["lon", "lat"])
nr_trail_df["iter"] = np.arange(len(nr_trail_df))
nr_trail_df.to_csv(TRAIL_NEWTON_CSV, index=False)

results_df = pd.DataFrame([
    {
        "method": r["method"],
        "lon_opt": r["x_opt"][0],
        "lat_opt": r["x_opt"][1],
        "f_opt": r["f_opt"],
        "iterations": r["iterations"],
        "grad_norm_final": r["grad_norm"],
        "elapsed_sec": r["elapsed_sec"],
    }
    for r in results
])
results_df.to_csv(RESULTS_CSV, index=False)

print(f"\nSaved gradient descent trail   -> {TRAIL_GD_CSV.name}  "
      f"({len(gd_trail_df)} steps)")
print(f"Saved Newton-Raphson trail     -> {TRAIL_NEWTON_CSV.name}  "
      f"({len(nr_trail_df)} steps)")
print(f"Saved solver comparison table  -> {RESULTS_CSV.name}")
print("\nReady for Session 004: visualize convergence trails on the HK map.")
