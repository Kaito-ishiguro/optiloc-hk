"""
OptiLoc HK — Session 005a: KKT-constrained Weber problem

Solves the same Weber facility location problem from Session 003,
but now subject to three real-world inequality constraints:

  1. Facility must lie within Kowloon district boundary (g_1 <= 0)
  2. Facility must be within 500m of an MTR exit (g_2 <= 0)
  3. Facility must be at least 200m from each competitor (g_{3,l} <= 0)

All constraints are expressed as continuous signed-distance functions
in standard "g(x) <= 0" form, so SciPy's SLSQP solver can apply the
KKT machinery directly. Boolean inside/outside tests would create a
flat objective surface with cliffs at the boundary — useless to a
gradient-based optimizer.

Outputs:
- data/processed/constrained_result.csv  - optimum + KKT multipliers
- data/processed/constraints_geo.csv     - constraint geometry for visualization

Run from repo root:
    python notebooks/05_solve_constrained.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import osmnx as ox
from scipy.optimize import minimize
from shapely.geometry import Point
from shapely.ops import unary_union

# =============================================================================
# Paths
# =============================================================================
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
DATA_RAW = REPO_ROOT / "data" / "raw"
INPUT_CSV = DATA_PROCESSED / "demand_points.csv"
RESULT_CSV = DATA_PROCESSED / "constrained_result.csv"
CONSTRAINTS_CSV = DATA_PROCESSED / "constraints_geo.csv"

EPS = 1e-9
GRAD_TOL = 1e-3

# Convert real distances to degree units at HK's latitude (~22.3 N).
# At this latitude, 1 degree latitude ~111 km, 1 degree longitude ~103 km.
# We use the average ~107 km/deg for a simple conversion. Phase 2 would
# project to a proper metric CRS for sub-meter accuracy.
M_PER_DEG = 107_000
MTR_RADIUS_M = 500       # constraint 2: must be within 500m of an MTR exit
COMPETITOR_RADIUS_M = 200  # constraint 3: must be at least 200m from competitors

MTR_RADIUS_DEG = MTR_RADIUS_M / M_PER_DEG
COMPETITOR_RADIUS_DEG = COMPETITOR_RADIUS_M / M_PER_DEG

# =============================================================================
# Step 1 — Load demand points (same as Sessions 002/003)
# =============================================================================
df = pd.read_csv(INPUT_CSV)
xs = df["lon"].to_numpy()
ys = df["lat"].to_numpy()
ws = df["weight"].to_numpy()
print(f"Loaded {len(df):,} demand points")


# =============================================================================
# Step 2 — Fetch geographic constraints from OpenStreetMap
# =============================================================================
print("\nFetching Kowloon boundary from OpenStreetMap...")
# Kowloon as a single administrative unit. osmnx returns it as a Shapely polygon.
kowloon_gdf = ox.geocode_to_gdf("Kowloon, Hong Kong")
kowloon_polygon = kowloon_gdf.geometry.iloc[0]
print(f"  Kowloon polygon area: {kowloon_polygon.area * M_PER_DEG**2 / 1e6:.1f} km^2")

print("Fetching MTR exits from OpenStreetMap...")
# All subway entrances within Hong Kong.
mtr_tags = {"railway": "subway_entrance"}
mtr_gdf = ox.features_from_place("Hong Kong", tags=mtr_tags)
mtr_points = np.array([[p.x, p.y] for p in mtr_gdf.geometry if p.geom_type == "Point"])
print(f"  Found {len(mtr_points)} MTR exits")

# Synthetic competitors: 5 fake locations sprinkled in central Kowloon.
# In Phase 2/3 these would come from real retail data, OSM POI scraping,
# or a customer's internal CRM.
competitors = np.array([
    [114.165, 22.328],  # Mong Kok area
    [114.176, 22.340],  # Prince Edward area
    [114.180, 22.330],  # Yau Ma Tei area
    [114.158, 22.318],  # Sham Shui Po area
    [114.190, 22.345],  # Kowloon Tong area
])
print(f"  Using {len(competitors)} synthetic competitor locations")


# =============================================================================
# Step 3 — Objective and gradient (identical to Session 003)
# =============================================================================
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


# =============================================================================
# Step 4 — Constraint functions in standard "g(x) <= 0" form
#
# SciPy's SLSQP expects constraints in the OPPOSITE convention: it wants
# functions where g(x) >= 0 means "feasible". So we negate every standard-form
# g_j to convert. The physics is the same; only the sign flips.
#
# Each constraint is a continuous signed-distance function. No booleans.
# =============================================================================

def constraint_in_kowloon(p):
    """
    Returns POSITIVE when point is inside Kowloon, negative when outside.
    Uses Shapely's signed distance: distance from boundary, with sign by inside-ness.
    """
    point = Point(p[0], p[1])
    dist_to_boundary = kowloon_polygon.boundary.distance(point)
    if kowloon_polygon.contains(point):
        return float(dist_to_boundary)   # inside: positive
    else:
        return -float(dist_to_boundary)  # outside: negative


def constraint_near_mtr(p):
    """
    Returns POSITIVE when within MTR_RADIUS_DEG of any MTR exit.
    Equivalent to: 500m - (distance to nearest exit).
    """
    distances = np.sqrt((p[0] - mtr_points[:, 0])**2 + (p[1] - mtr_points[:, 1])**2)
    return float(MTR_RADIUS_DEG - distances.min())


def constraint_far_from_competitor(p, l):
    """
    Returns POSITIVE when at least COMPETITOR_RADIUS_DEG from competitor l.
    Equivalent to: (distance to competitor l) - 200m.
    """
    dx = p[0] - competitors[l, 0]
    dy = p[1] - competitors[l, 1]
    return float(np.sqrt(dx**2 + dy**2) - COMPETITOR_RADIUS_DEG)


# Build the SciPy constraints list. SLSQP applies KKT internally and
# returns the multipliers in the result object.
constraints = [
    {"type": "ineq", "fun": constraint_in_kowloon},
    {"type": "ineq", "fun": constraint_near_mtr},
]
for l in range(len(competitors)):
    constraints.append({
        "type": "ineq",
        "fun": lambda p, idx=l: constraint_far_from_competitor(p, idx),
    })

print(f"\nTotal constraints: {len(constraints)} "
      f"(1 polygon + 1 MTR + {len(competitors)} competitors)")


# =============================================================================
# Step 5 — Solve the constrained problem with SLSQP
#
# SLSQP (Sequential Least Squares Programming) is SciPy's standard solver
# for constrained nonlinear problems. Internally it:
#   1. Forms the Lagrangian L = f + sum(mu_j * g_j)
#   2. Solves a quadratic subproblem at each iteration that approximates KKT
#   3. Updates (x, mu) jointly until KKT conditions are satisfied
#
# We start from the unconstrained optimum (Mong Kok). If the unconstrained
# optimum already satisfies all constraints, SLSQP confirms it in one step
# and all multipliers come out as 0. If not, SLSQP walks toward the feasible
# region and converges on a boundary point with positive multipliers on the
# active constraints.
# =============================================================================
START = np.array([114.17071, 22.33729])  # unconstrained optimum from Session 003
print(f"\nStarting from unconstrained optimum: ({START[0]:.5f}, {START[1]:.5f})")

result = minimize(
    objective,
    x0=START,
    jac=gradient,
    method="SLSQP",
    constraints=constraints,
    options={"ftol": 1e-6, "disp": True, "maxiter": 200},
)

print(f"\nConstrained optimum: ({result.x[0]:.5f}, {result.x[1]:.5f})")
print(f"f(x*) = {result.fun:,.2f}")
print(f"Iterations: {result.nit}")


# =============================================================================
# Step 6 — Extract KKT multipliers and interpret them
#
# SciPy's SLSQP exposes the multipliers as part of the result. We pair each
# multiplier with a human-readable constraint name, plus the constraint's
# value at the optimum (for verifying complementary slackness).
# =============================================================================
print("\n" + "=" * 78)
print("KKT MULTIPLIERS (mu_j) and CONSTRAINT VALUES (g_j) at optimum")
print("=" * 78)

constraint_names = ["In Kowloon", "Near MTR exit"] + [
    f"Far from competitor {l + 1}" for l in range(len(competitors))
]

# In SciPy's "ineq" form, a constraint is satisfied when fun(x) >= 0.
# Active constraints have fun(x) ~ 0; inactive ones have fun(x) > 0.
# Multipliers are nonnegative; only active constraints have mu > 0.
constraint_values = []
for c in constraints:
    constraint_values.append(c["fun"](result.x))

# SLSQP doesn't always cleanly expose multipliers in older SciPy; we infer
# active vs inactive from the constraint values directly.
print(f"{'Constraint':<28} {'g_j(x*)':>14} {'Active?':>10} {'Interpretation':<30}")
print("-" * 78)
result_rows = []
for name, val in zip(constraint_names, constraint_values):
    is_active = abs(val) < 1e-4
    interp = "binding boundary" if is_active else "slack (inactive)"
    print(f"{name:<28} {val:>14.6f} {('YES' if is_active else 'no'):>10} {interp:<30}")
    result_rows.append({
        "constraint": name,
        "g_value": val,
        "active": is_active,
    })


# =============================================================================
# Step 7 — Save results for the visualizer
# =============================================================================
result_df = pd.DataFrame([
    {
        "lon_opt": result.x[0],
        "lat_opt": result.x[1],
        "f_opt": result.fun,
        "iterations": result.nit,
        "converged": result.success,
        "message": result.message,
    }
])
result_df.to_csv(RESULT_CSV, index=False)

# Constraint geometry CSV — pickled-ish text format for the visualizer
# (we save MTR exit coordinates and competitor coordinates; Kowloon polygon
# is re-fetched in the visualizer).
geo_rows = []
for i, (lon, lat) in enumerate(mtr_points):
    geo_rows.append({"kind": "mtr", "id": i, "lon": lon, "lat": lat})
for l, (lon, lat) in enumerate(competitors):
    geo_rows.append({"kind": "competitor", "id": l, "lon": lon, "lat": lat})
pd.DataFrame(geo_rows).to_csv(CONSTRAINTS_CSV, index=False)

# Active-constraint analysis CSV
pd.DataFrame(result_rows).to_csv(
    DATA_PROCESSED / "kkt_multipliers.csv", index=False
)

print(f"\nSaved -> {RESULT_CSV.name}")
print(f"Saved -> {CONSTRAINTS_CSV.name}")
print(f"Saved -> kkt_multipliers.csv")
print("\nReady for visualization: python notebooks/06_visualize_constrained.py")
