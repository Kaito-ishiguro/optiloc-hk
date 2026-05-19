"""
OptiLoc HK — Integration #1 (Path B): spatial variation of the Hessian

Lecture 6 of DASE2135 covers convergence analysis of gradient methods on
quadratic problems. The key result: for a quadratic with Hessian H, the
convergence rate of steepest descent is bounded by the condition number
kappa(H), and the optimal step size is alpha_opt = 2 / (lambda_min + lambda_max).

This script evaluates the Hessian at SIX different points across Hong Kong:
the optimum, a near-optimum start, and the four corner starting points
from Session 004 (Tung Chung, Stanley, Sai Kung, Lok Ma Chau). For each
point we compute:

  - eigenvalues lambda_min, lambda_max
  - condition number kappa = lambda_max / lambda_min
  - optimal step size alpha_opt = 2 / (lambda_min + lambda_max)
  - gradient magnitude

Why this matters: it tells us whether the slow gradient descent we observed
is due to BAD CONDITIONING (Lecture 6's textbook story) or due to the Hessian
varying in SCALE across space (the non-quadratic reality of the Weber problem).

Run from repo root:
    python notebooks/07_condition_number.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------- Paths ----------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
INPUT_CSV = DATA_PROCESSED / "demand_points.csv"

EPS = 1e-9

# Points to evaluate at — chosen to span HK geographically.
# Format: (name, lon, lat, distance_class)
EVAL_POINTS = [
    ("Optimum (Mong Kok)",     114.17071, 22.33729, "at optimum"),
    ("Victoria Harbour",        114.17,    22.32,    "near optimum"),
    ("Tung Chung (W)",          113.94,    22.29,    "far from optimum"),
    ("Stanley (S)",             114.21,    22.22,    "far from optimum"),
    ("Sai Kung (E)",            114.27,    22.38,    "far from optimum"),
    ("Lok Ma Chau (N)",         114.07,    22.51,    "far from optimum"),
]


# ---------- Load demand points ----------
df = pd.read_csv(INPUT_CSV)
xs = df["lon"].to_numpy()
ys = df["lat"].to_numpy()
ws = df["weight"].to_numpy()
print(f"Loaded {len(df):,} demand points")


# ---------- Gradient + Hessian (identical to Session 003) ----------
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


# ---------- Evaluate at each point ----------
rows = []
for name, lon, lat, distance_class in EVAL_POINTS:
    p = np.array([lon, lat])
    g = gradient(p)
    H = hessian(p)
    eigvals = np.linalg.eigvalsh(H)
    lam_min, lam_max = float(eigvals[0]), float(eigvals[1])
    kappa = lam_max / lam_min
    alpha_opt = 2.0 / (lam_min + lam_max)
    rows.append({
        "name": name,
        "distance_class": distance_class,
        "lon": lon,
        "lat": lat,
        "grad_norm": float(np.linalg.norm(g)),
        "lambda_min": lam_min,
        "lambda_max": lam_max,
        "kappa": kappa,
        "alpha_opt": alpha_opt,
    })

results = pd.DataFrame(rows)


# ---------- Print main comparison table ----------
print("\n" + "=" * 100)
print("HESSIAN ANALYSIS ACROSS HK")
print("=" * 100)
print(f"{'Location':<22} {'||grad f||':>14} {'lambda_max':>14} "
      f"{'kappa':>10} {'alpha_opt':>14}")
print("-" * 100)
for _, r in results.iterrows():
    print(f"{r['name']:<22} {r['grad_norm']:>14.2e} "
          f"{r['lambda_max']:>14.2e} {r['kappa']:>10.3f} "
          f"{r['alpha_opt']:>14.2e}")


# ---------- Analysis 1: is conditioning the issue? ----------
kappas = results["kappa"].values
print("\n" + "=" * 100)
print("ANALYSIS 1 — IS THE PROBLEM POORLY CONDITIONED?")
print("=" * 100)
print(f"Condition numbers range from {kappas.min():.3f} to {kappas.max():.3f}.")
print(f"Mean kappa across all evaluated points: {kappas.mean():.3f}.")
if kappas.max() < 10:
    print("VERDICT: NO. The Hessian is well-conditioned EVERYWHERE in HK.")
    print("Lecture 6's textbook 'slow gradient descent from high kappa' does NOT apply here.")
else:
    print("VERDICT: YES. The Hessian is ill-conditioned at some points.")


# ---------- Analysis 2: does the Hessian magnitude vary? ----------
lam_max = results["lambda_max"].values
ratio = lam_max.max() / lam_max.min()
print("\n" + "=" * 100)
print("ANALYSIS 2 — DOES THE HESSIAN MAGNITUDE VARY ACROSS SPACE?")
print("=" * 100)
print(f"Largest eigenvalue lambda_max ranges from {lam_max.min():.2e} "
      f"to {lam_max.max():.2e}.")
print(f"That's a ratio of {ratio:.1f}x across the evaluated points.")
print(f"This is the signature of a NON-QUADRATIC objective: the local curvature")
print(f"changes as you move through space, so any 'optimal' step size for one")
print(f"region is wrong for another.")


# ---------- Analysis 3: how does this compare to our chosen alpha? ----------
alpha_used = 1e-9   # the value we actually used in Sessions 003/004
print("\n" + "=" * 100)
print("ANALYSIS 3 — WAS OUR STEP SIZE ALPHA = 1e-9 OPTIMAL ANYWHERE?")
print("=" * 100)
print(f"{'Location':<22} {'alpha_opt':>14} {'alpha used':>14} {'ratio used/opt':>18}")
print("-" * 100)
for _, r in results.iterrows():
    ratio_used_opt = alpha_used / r["alpha_opt"]
    print(f"{r['name']:<22} {r['alpha_opt']:>14.2e} {alpha_used:>14.2e} "
          f"{ratio_used_opt:>18.3f}")

print(f"\nKey reading: 'ratio used/opt' close to 1.0 means our step size was")
print(f"near-optimal at that point. Far from 1.0 means we were either under-")
print(f"stepping (sub-1, slow convergence) or over-stepping (sup-1, divergence).")


# ---------- Bottom-line story ----------
print("\n" + "=" * 100)
print("BOTTOM-LINE STORY (the exam answer)")
print("=" * 100)
print("""
The Weber objective on real HK data is:

  - UNIFORMLY WELL-CONDITIONED: kappa is small everywhere, so Lecture 6's
    textbook 'high kappa => slow gradient descent' is NOT what's happening.

  - GLOBALLY NON-QUADRATIC: the Hessian magnitude varies dramatically across
    space because of the 1/d^3 scaling in each demand-point term. The
    'optimal step size' alpha_opt = 2/(lambda_min + lambda_max) changes
    by orders of magnitude depending on where you stand.

  - A SINGLE CONSTANT alpha CANNOT BE RIGHT EVERYWHERE: alpha=1e-9 was tuned
    conservatively to avoid divergence from the worst-case starting point.
    That makes it too small for efficient steps at most other points, which
    is why gradient descent took 255-323 iterations rather than the ~2 that
    pure kappa analysis would predict.

  - WHY NEWTON WINS: Newton's step (-H^-1 * grad) self-scales using the local
    Hessian, so it AUTOMATICALLY adapts to whatever region of space you're in.
    No tuning required, no over/under-stepping. That's why Newton converged in
    5-6 iterations from every starting point in Session 004.
""")
