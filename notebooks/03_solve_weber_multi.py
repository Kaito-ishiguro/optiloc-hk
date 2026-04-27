"""
OptiLoc HK — Session 004a: multi-start solver

Runs gradient descent and Newton-Raphson from 4 different starting points
across Hong Kong, saving all convergence trails to a single CSV for the
visualization in 04_visualize_convergence.py.

The math, the gradient/Hessian, and the algorithms are identical to
Session 003. The only change is wrapping the solvers in a loop over
multiple starting points so we can show that all paths converge to the
same global optimum (visual proof of the convex objective).

Run from repo root:
    python notebooks/03_solve_weber_multi.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------- Paths ----------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
INPUT_CSV = DATA_PROCESSED / "demand_points.csv"
TRAILS_CSV = DATA_PROCESSED / "trails_multistart.csv"

EPS = 1e-9
GRAD_TOL = 1e-3

# ---------- Load demand points (same as Session 003) ----------
df = pd.read_csv(INPUT_CSV)
xs = df["lon"].to_numpy()
ys = df["lat"].to_numpy()
ws = df["weight"].to_numpy()
n = len(df)
print(f"Loaded {n:,} demand points (total weight: {ws.sum():,.0f})")

# ---------- 4 starting points across HK ----------
# Chosen to span the territory geographically so the convergence story is visual.
STARTING_POINTS = [
    {"name": "Tung Chung",   "lon": 113.94, "lat": 22.29, "color": "#E63946"},  # red
    {"name": "Stanley",      "lon": 114.21, "lat": 22.22, "color": "#2A9D8F"},  # teal
    {"name": "Sai Kung",     "lon": 114.27, "lat": 22.38, "color": "#F4A261"},  # orange
    {"name": "Lok Ma Chau",  "lon": 114.07, "lat": 22.51, "color": "#7B2CBF"},  # purple
]


# ---------- Math (vectorized NumPy, identical to Session 003) ----------
def objective(p):
    dx = p[0] - xs
    dy = p[1] - ys
    d = np.sqrt(dx**2 + dy**2 + EPS)
    return float(np.sum(ws * d))


def gradient(p):
    dx = p[0] - xs
    dy = p[1] - ys
    d = np.sqrt(dx**2 + dy**2 + EPS)
    coef = ws / d
    return np.array([np.sum(coef * dx), np.sum(coef * dy)])


def hessian(p):
    dx = p[0] - xs
    dy = p[1] - ys
    d = np.sqrt(dx**2 + dy**2 + EPS)
    coef = ws / (d**3)
    H_xx = np.sum(coef * dy**2)
    H_yy = np.sum(coef * dx**2)
    H_xy = -np.sum(coef * dx * dy)
    return np.array([[H_xx, H_xy], [H_xy, H_yy]])


# ---------- Solvers (identical to Session 003, just return the trail) ----------
def gradient_descent(start, alpha=1e-9, max_iter=10_000, tol=GRAD_TOL):
    p = np.array(start, dtype=float)
    trail = [p.copy()]
    for _ in range(max_iter):
        g = gradient(p)
        if np.linalg.norm(g) < tol:
            break
        p = p - alpha * g
        trail.append(p.copy())
    return np.array(trail)


def newton_raphson(start, max_iter=100, tol=GRAD_TOL):
    p = np.array(start, dtype=float)
    trail = [p.copy()]
    for _ in range(max_iter):
        g = gradient(p)
        if np.linalg.norm(g) < tol:
            break
        H = hessian(p)
        try:
            step = np.linalg.solve(H, -g)
        except np.linalg.LinAlgError:
            break  # Hessian became singular; stop
        # Backtracking line search: halve the step until objective improves
        f_current = objective(p)
        alpha = 1.0
        for _ in range(30):
            p_trial = p + alpha * step
            if objective(p_trial) < f_current:
                p = p_trial
                break
            alpha *= 0.5
        else:
            break  # No improvement found in 30 tries; stop
        trail.append(p.copy())
    return np.array(trail)


# ---------- Run both solvers from each starting point ----------
all_rows = []
print("\nRunning solvers from 4 starting points...\n")
print(f"{'Start':<14} {'Method':<18} {'Iters':>8} {'Final lon':>11} {'Final lat':>11}")
print("-" * 64)

for sp in STARTING_POINTS:
    start = [sp["lon"], sp["lat"]]

    # Gradient descent
    trail_gd = gradient_descent(start)
    for k, (lon, lat) in enumerate(trail_gd):
        all_rows.append({
            "start_name": sp["name"],
            "color": sp["color"],
            "method": "Gradient Descent",
            "iter": k,
            "lon": lon,
            "lat": lat,
        })
    print(f"{sp['name']:<14} {'Gradient Descent':<18} {len(trail_gd) - 1:>8} "
          f"{trail_gd[-1, 0]:>11.5f} {trail_gd[-1, 1]:>11.5f}")

    # Newton-Raphson
    trail_nr = newton_raphson(start)
    for k, (lon, lat) in enumerate(trail_nr):
        all_rows.append({
            "start_name": sp["name"],
            "color": sp["color"],
            "method": "Newton-Raphson",
            "iter": k,
            "lon": lon,
            "lat": lat,
        })
    print(f"{sp['name']:<14} {'Newton-Raphson':<18} {len(trail_nr) - 1:>8} "
          f"{trail_nr[-1, 0]:>11.5f} {trail_nr[-1, 1]:>11.5f}")

# ---------- Save consolidated trails CSV ----------
trails_df = pd.DataFrame(all_rows)
trails_df.to_csv(TRAILS_CSV, index=False)
print(f"\nSaved {len(trails_df):,} trail points across "
      f"{len(STARTING_POINTS)} start points x 2 methods")
print(f"  -> {TRAILS_CSV}")
print("\nReady for visualization: run python notebooks/04_visualize_convergence.py")

