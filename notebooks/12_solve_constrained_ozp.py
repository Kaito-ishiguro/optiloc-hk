"""
notebooks/12_solve_constrained_ozp.py

Solve the Weber facility location problem subject to a single
realistic constraint: the facility must be located inside the
union of all Commercial (C) and Comprehensive Development Area
(CDA) zoning polygons in Hong Kong's Outline Zoning Plans.

This replaces Session 005's "must be inside the Kowloon polygon"
constraint with something ~5x more restrictive and 499x more
topologically complex. Compares the new optimum against the
unconstrained (Session 003) and Kowloon-constrained (Session 005)
answers.

MTR-proximity and competitor-exclusion constraints from Session 005
are intentionally dropped here. They were inactive in Session 005
(all KKT multipliers zero), so dropping them keeps the comparison
clean: any movement in the optimum is purely due to the OZP swap.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.optimize import minimize
from shapely.geometry import Point

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
DEMAND_PATH = DATA_DIR / "demand_points.csv"
UNION_PATH  = DATA_DIR / "ozp_commercial_union.geojson"
OUTPUT_PATH = DATA_DIR / "ozp_constrained_result.csv"

EPS = 1e-9  # avoid div-by-zero at demand points


# ---------- Weber objective + gradient ----------

def weber_objective(x, points, weights):
    diffs = points - x
    dists = np.sqrt((diffs ** 2).sum(axis=1) + EPS)
    return float((weights * dists).sum())


def weber_gradient(x, points, weights):
    diffs = x - points
    dists = np.sqrt((diffs ** 2).sum(axis=1) + EPS)
    return (weights[:, None] * diffs / dists[:, None]).sum(axis=0)


# ---------- OZP feasibility constraint ----------

def make_ozp_constraint(union_geom):
    """
    Returns g(x) where:
       g(x) > 0  iff x is inside the commercial union (feasible)
       g(x) < 0  iff x is outside                       (infeasible)
       g(x) = 0  on the boundary

    SLSQP's {'type':'ineq'} convention is fun(x) >= 0 means feasible,
    so the signed-distance form gives the optimizer a continuous
    gradient pointing toward feasibility -- exactly as in Session 005,
    just over a 499-piece MultiPolygon instead of a single polygon.
    """
    boundary = union_geom.boundary

    def g(x):
        p = Point(float(x[0]), float(x[1]))
        if union_geom.contains(p):
            return float(boundary.distance(p))   # +ve depth into feasible region
        return float(-union_geom.distance(p))    # -ve distance back to feasibility
    return g


# ---------- Solve ----------

def main():
    print(f"Loading demand points from {DEMAND_PATH.name} ...")
    demand = pd.read_csv(DEMAND_PATH)
    points  = demand[["lon", "lat"]].values.astype(float)
    weights = demand["weight"].values.astype(float)
    print(f"  {len(demand):,} demand points, total weight {weights.sum():,.0f}")

    print(f"Loading OZP commercial union from {UNION_PATH.name} ...")
    ozp_gdf = gpd.read_file(UNION_PATH)
    union_geom = ozp_gdf.iloc[0].geometry
    print(f"  {len(union_geom.geoms)} disjoint polygons, "
          f"{ozp_gdf.iloc[0]['total_area_km2']} km^2")

    g_ozp = make_ozp_constraint(union_geom)

    x0 = np.array([114.17, 22.32])   # Victoria Harbour, same start as Session 005
    print(f"\nStarting point: lon={x0[0]:.5f}, lat={x0[1]:.5f}")
    print(f"  g_ozp(x0) = {g_ozp(x0):+.6f}  "
          f"({'inside' if g_ozp(x0) >= 0 else 'outside'} feasible region)")

    constraints = [{"type": "ineq", "fun": g_ozp}]

    print("\nRunning SLSQP ...")
    result = minimize(
        weber_objective,
        x0,
        args=(points, weights),
        jac=weber_gradient,
        method="SLSQP",
        constraints=constraints,
        options={"disp": True, "maxiter": 200, "ftol": 1e-9},
    )

    print(f"\n  Converged:   {result.success}")
    print(f"  Iterations:  {result.nit}")
    print(f"  Optimum:     lon={result.x[0]:.6f}, lat={result.x[1]:.6f}")
    print(f"  Objective:   {result.fun:.4f}")
    print(f"  g_ozp(x*):   {g_ozp(result.x):+.6e}  "
          f"(near 0 => on boundary; positive => interior)")

    # Three-way comparison
    print("\nComparison:")
    print(f"  Unconstrained (Session 003):  (114.17071, 22.33729)  Mong Kok / Prince Edward")
    print(f"  Kowloon-constrained (S 005):  (114.17323, 22.34038)  Kowloon historical boundary")
    print(f"  OZP-constrained (this run):   ({result.x[0]:.5f}, {result.x[1]:.5f})")

    # Shift from unconstrained, rough conversion to meters at HK latitude
    unc = np.array([114.17071, 22.33729])
    shift_deg = float(np.linalg.norm(result.x - unc))
    shift_m   = shift_deg * 111_000
    print(f"\n  Shift from unconstrained optimum: "
          f"{shift_deg:.5f} deg  (~ {shift_m:.0f} m on the ground)")

    # Persist
    pd.DataFrame({
        "method":        ["SLSQP_OZP"],
        "lon":           [result.x[0]],
        "lat":           [result.x[1]],
        "objective":     [result.fun],
        "iterations":    [result.nit],
        "success":       [result.success],
        "g_ozp_at_opt":  [g_ozp(result.x)],
    }).to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved result to {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()