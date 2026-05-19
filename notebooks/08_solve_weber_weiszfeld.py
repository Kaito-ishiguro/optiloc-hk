"""
Session 008 — Weiszfeld algorithm for the Weber problem.

Implements the classical FONC-derived fixed-point iteration:

    x^(k+1) = sum_i (w_i / d_i^(k)) * x_i  /  sum_i (w_i / d_i^(k))

where d_i^(k) = ||x^(k) - x_i||.

This is the algorithm Prof. Kuo flagged in his email: derived from the
first-order necessary condition (FONC) you learned in DASE2135 by
algebraically rearranging the gradient equation grad f = 0 into a
fixed-point form, then iterating it.

Compares against the three solvers from Session 003 (gradient descent,
Newton-Raphson, SciPy BFGS) and prints a four-solver summary table.
"""

import time

import numpy as np
import pandas as pd
from scipy.optimize import minimize


# ---------------------------------------------------------------------------
# Math constants
# ---------------------------------------------------------------------------

EPS = 1e-9            # avoids d_i = 0 singularity at demand points
TOL = 1e-8            # convergence tolerance on ||x^(k+1) - x^(k)||
MAX_ITER = 1000       # safety cap; Weiszfeld typically converges in 30-80
START = np.array([114.17, 22.32])  # Victoria Harbour, near the optimum


# ---------------------------------------------------------------------------
# Vectorized objective + gradient (shared with all solvers for fair comparison)
# ---------------------------------------------------------------------------

def objective(x, points, weights):
    """Weber objective: f(x) = sum_i w_i * ||x - x_i||."""
    diffs = points - x
    dists = np.sqrt((diffs ** 2).sum(axis=1) + EPS)
    return float((weights * dists).sum())


def gradient(x, points, weights):
    """Gradient: grad f = sum_i (w_i / d_i) * (x - x_i)."""
    diffs = x - points
    dists = np.sqrt((diffs ** 2).sum(axis=1) + EPS)
    return (weights[:, None] * diffs / dists[:, None]).sum(axis=0)


def hessian(x, points, weights):
    """Hessian: sum_i (w_i / d_i^3) * [[(y-y_i)^2, -(x-x_i)(y-y_i)], ...]."""
    diffs = x - points
    dx = diffs[:, 0]
    dy = diffs[:, 1]
    d = np.sqrt(dx * dx + dy * dy + EPS)
    d3 = d ** 3
    h00 = (weights * dy * dy / d3).sum()
    h11 = (weights * dx * dx / d3).sum()
    h01 = -(weights * dx * dy / d3).sum()
    return np.array([[h00, h01], [h01, h11]])


# ---------------------------------------------------------------------------
# Solver 1: Weiszfeld (the new one)
# ---------------------------------------------------------------------------

def weiszfeld(points, weights, x0, tol=TOL, max_iter=MAX_ITER):
    """
    Fixed-point iteration:
        x_new = sum_i (w_i / d_i) * x_i  /  sum_i (w_i / d_i)

    Each step is a weighted average of demand points, weighted by inverse
    current distance. No step size, no Hessian inversion, no line search.
    """
    x = np.array(x0, dtype=float)
    trail = [x.copy()]
    for k in range(max_iter):
        diffs = points - x
        dists = np.sqrt((diffs ** 2).sum(axis=1) + EPS)
        u = weights / dists                         # inverse-distance weights
        x_new = (points * u[:, None]).sum(axis=0) / u.sum()
        trail.append(x_new.copy())
        if np.linalg.norm(x_new - x) < tol:
            return x_new, k + 1, np.array(trail)
        x = x_new
    return x, max_iter, np.array(trail)


# ---------------------------------------------------------------------------
# Solver 2: Gradient descent (Session 003 baseline)
# ---------------------------------------------------------------------------

def gradient_descent(points, weights, x0, alpha=1e-9, tol=1e-3, max_iter=10_000):
    x = np.array(x0, dtype=float)
    trail = [x.copy()]
    for k in range(max_iter):
        g = gradient(x, points, weights)
        if np.linalg.norm(g) < tol:
            return x, k + 1, np.array(trail)
        x = x - alpha * g
        trail.append(x.copy())
    return x, max_iter, np.array(trail)


# ---------------------------------------------------------------------------
# Solver 3: Newton-Raphson (Session 003 baseline)
# ---------------------------------------------------------------------------

def newton(points, weights, x0, tol=TOL, max_iter=100):
    x = np.array(x0, dtype=float)
    trail = [x.copy()]
    for k in range(max_iter):
        g = gradient(x, points, weights)
        H = hessian(x, points, weights)
        try:
            step = np.linalg.solve(H, -g)
        except np.linalg.LinAlgError:
            return x, k + 1, np.array(trail)  # singular Hessian fallback
        x_new = x + step
        trail.append(x_new.copy())
        if np.linalg.norm(x_new - x) < tol:
            return x_new, k + 1, np.array(trail)
        x = x_new
    return x, max_iter, np.array(trail)


# ---------------------------------------------------------------------------
# Solver 4: SciPy BFGS (cross-validation reference)
# ---------------------------------------------------------------------------

def bfgs(points, weights, x0):
    trail = [np.array(x0, dtype=float)]

    def record(xk):
        trail.append(xk.copy())

    result = minimize(
        objective,
        x0,
        args=(points, weights),
        jac=gradient,
        method="BFGS",
        options={"gtol": TOL},
        callback=record,
    )
    return result.x, result.nit, np.array(trail)


# ---------------------------------------------------------------------------
# Main: run all four, print comparison
# ---------------------------------------------------------------------------

def main():
    print("Loading demand points...")
    df = pd.read_csv("data/processed/demand_points.csv")
    points = df[["lon", "lat"]].to_numpy()
    weights = df["weight"].to_numpy()
    print(f"  {len(points):,} demand points, total weight {weights.sum():,.0f}\n")

    solvers = [
        ("Weiszfeld",  lambda: weiszfeld(points, weights, START)),
        ("Newton",     lambda: newton(points, weights, START)),
        ("BFGS",       lambda: bfgs(points, weights, START)),
        ("GD",         lambda: gradient_descent(points, weights, START)),
    ]

    results = []
    all_trails = []
    for name, fn in solvers:
        t0 = time.perf_counter()
        x_star, iters, trail = fn()
        elapsed = time.perf_counter() - t0
        f_star = objective(x_star, points, weights)
        results.append({
            "method": name,
            "lon":    x_star[0],
            "lat":    x_star[1],
            "iters":  iters,
            "time_s": elapsed,
            "f_star": f_star,
        })
        for k, (lon, lat) in enumerate(trail):
            all_trails.append({"method": name, "iter": k, "lon": lon, "lat": lat})

    print(f"{'Method':<12} {'lon':>12} {'lat':>12} {'iters':>7} {'time (s)':>10} {'f*':>16}")
    print("-" * 72)
    for r in results:
        print(
            f"{r['method']:<12} "
            f"{r['lon']:>12.8f} "
            f"{r['lat']:>12.8f} "
            f"{r['iters']:>7d} "
            f"{r['time_s']:>10.4f} "
            f"{r['f_star']:>16.4f}"
        )

    coords = np.array([[r["lon"], r["lat"]] for r in results])
    spread = np.linalg.norm(coords - coords[0], axis=1).max()
    print(f"\nMax disagreement between solvers: {spread:.2e} degrees")
    if spread < 1e-6:
        print("All four solvers converged to the same Mong Kok optimum.")
    else:
        print("WARNING: solvers disagree by more than 1e-6 degrees - investigate.")

    out = pd.DataFrame(results)
    out.to_csv("data/processed/solver_comparison.csv", index=False)
    print("\nSaved comparison table to data/processed/solver_comparison.csv")

    trails_df = pd.DataFrame(all_trails)
    trails_df.to_csv("data/processed/four_solver_trails.csv", index=False)
    print(f"Saved {len(trails_df):,} trail points to data/processed/four_solver_trails.csv")


if __name__ == "__main__":
    main()