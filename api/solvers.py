"""Solver wrappers for the OptiLoc API.

Loads the numbered notebook scripts (files 08 and 16) as modules via
importlib.util — the same pattern Session 013 used in file 18 to reuse
file 16's Lloyd machinery. Notebooks remain the single source of truth for
solver math.

Data assets (demand points CSV, OZP commercial union GeoJSON) are loaded
once into a process-wide cache at startup, then reused across requests.
"""

import importlib.util
import time
from types import ModuleType

import geopandas as gpd
import numpy as np
import pandas as pd

from api.config import (
    BUFFER_DEG,
    DEMAND_CSV,
    KMEDIAN_SOLVER_PATH,
    OZP_GEOJSON,
    RNG_SEED,
    WEBER_SOLVER_PATH,
    WEISZFELD_START_LAT,
    WEISZFELD_START_LON,
)


# ---- importlib module loader --------------------------------------------------

def _load_module_from_path(name: str, path) -> ModuleType:
    """Load a Python file as a module; needed because notebook files start
    with digits (e.g. '08_solve_weber_weiszfeld.py') which can't be regular
    imports. Same pattern as notebooks/18_ksweep_ozp.py."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Process-wide cache, populated by initialize_solvers() at FastAPI startup.
_weber_mod: ModuleType | None = None
_kmedian_mod: ModuleType | None = None
_demand_points: np.ndarray | None = None
_weights: np.ndarray | None = None
_ozp_geom = None  # Buffered shapely (Multi)Polygon.


def initialize_solvers() -> None:
    """Load notebook modules and data assets once. Called from FastAPI lifespan."""
    global _weber_mod, _kmedian_mod, _demand_points, _weights, _ozp_geom

    _weber_mod = _load_module_from_path("weber_mod", WEBER_SOLVER_PATH)
    _kmedian_mod = _load_module_from_path("kmedian_mod", KMEDIAN_SOLVER_PATH)

    df = pd.read_csv(DEMAND_CSV)
    _demand_points = df[["lon", "lat"]].to_numpy(dtype=float)
    _weights = df["weight"].to_numpy(dtype=float)

    ozp_gdf = gpd.read_file(OZP_GEOJSON)
    _ozp_geom = ozp_gdf.iloc[0].geometry.buffer(BUFFER_DEG)


# ---- /solve_weber wrapper -----------------------------------------------------

def solve_weber() -> dict:
    """Run Weiszfeld from the baked-in Victoria Harbour start on HK demand."""
    assert _weber_mod is not None and _demand_points is not None
    x0 = np.array([WEISZFELD_START_LON, WEISZFELD_START_LAT])

    t0 = time.perf_counter()
    x_star, iters, _trail = _weber_mod.weiszfeld(_demand_points, _weights, x0)
    elapsed = time.perf_counter() - t0

    f_star = _weber_mod.objective(x_star, _demand_points, _weights)
    return {
        "lon": float(x_star[0]),
        "lat": float(x_star[1]),
        "objective": float(f_star),
        "iterations": int(iters),
        "runtime_s": elapsed,
        "n_demand_points": int(len(_demand_points)),
        "total_weight": float(_weights.sum()),
    }


# ---- /solve_kmedian_ozp wrapper -----------------------------------------------

def solve_kmedian_ozp(k: int, n_restarts: int) -> dict:
    """Run k-median with OZP commercial constraint over n_restarts random inits.
    Reuses Session 012's lloyd_one_restart from file 16."""
    assert (
        _kmedian_mod is not None
        and _demand_points is not None
        and _ozp_geom is not None
    )
    rng = np.random.default_rng(RNG_SEED)

    t0 = time.perf_counter()
    results = []
    for r in range(1, n_restarts + 1):
        res = _kmedian_mod.lloyd_one_restart(
            _demand_points, _weights, _ozp_geom, k, rng, r
        )
        results.append(res)
    total_t = time.perf_counter() - t0

    best = min(results, key=lambda r: r["final_obj"])
    best_obj = best["final_obj"]
    worst_obj = max(r["final_obj"] for r in results)
    gap_pct = 100.0 * (worst_obj - best_obj) / best_obj if best_obj > 0 else 0.0
    distinct = {round(r["final_obj"], 0) for r in results}

    return {
        "k": k,
        "n_restarts": n_restarts,
        "best_objective": float(best_obj),
        "worst_objective": float(worst_obj),
        "worst_best_gap_pct": float(gap_pct),
        "n_distinct_optima": len(distinct),
        "facilities": [
            {"lon": float(lon), "lat": float(lat)}
            for lon, lat in best["facilities"]
        ],
        "restarts": [
            {
                "restart_id": r["restart_id"],
                "final_obj": float(r["final_obj"]),
                "n_lloyd_iters": int(r["n_lloyd_iters"]),
                "converged": bool(r["converged"]),
                "slsqp_calls": int(r["slsqp_calls"]),
                "weiszfeld_calls": int(r["weiszfeld_calls"]),
            }
            for r in results
        ],
        "runtime_s": total_t,
    }
