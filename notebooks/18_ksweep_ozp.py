"""
notebooks/18_ksweep_ozp.py

Session 013: k-sweep diminishing returns for OZP-constrained k-median.

Reuses Session 012's Lloyd + Weiszfeld + SLSQP machinery from
notebooks/16_solve_kmedian_ozp.py. Wraps it in an outer k-loop over
k in {3, 5, 8, 10, 15, 20}. For each k, runs N_RESTARTS multi-start
and records best/worst/mean objective, multi-start gap, convergence
counts, and total runtime.

Fresh RNG(seed=42) per k -> k=5 sub-run exactly reproduces Session 012.
Summary CSV is rewritten after each k completes (crash-safe checkpoint).

Output drives the headline chart on the Phase 1 landing page:
"how many hubs is enough for HK?"
"""

import time
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

# ---------- Load Session 012 module (filename starts with digit -> importlib) ----------
_THIS = Path(__file__).parent
_spec = importlib.util.spec_from_file_location(
    "sess12", _THIS / "16_solve_kmedian_ozp.py"
)
sess12 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sess12)

# ---------- Sweep config ----------
K_VALUES = [3, 5, 8, 10, 15, 20]
N_RESTARTS = 10          # matches Session 012 for apples-to-apples comparison
RNG_SEED = 42            # fresh RNG per k for reproducibility

DATA_DIR = Path("data/processed")
DEMAND_CSV = DATA_DIR / "demand_points.csv"
OZP_GEOJSON = DATA_DIR / "ozp_commercial_union.geojson"
OUT_SUMMARY = DATA_DIR / "ksweep_ozp_summary.csv"
OUT_ALL = DATA_DIR / "ksweep_ozp_all_restarts.csv"
OUT_BEST_FAC = DATA_DIR / "ksweep_ozp_best_facilities.csv"

BASELINE_SINGLE = 671_466.0  # Session 003 single-facility Weber objective


def main():
    print("=" * 64)
    print("Session 013: k-sweep diminishing returns (OZP-constrained)")
    print("=" * 64)

    print(f"\nLoading demand points from {DEMAND_CSV} ...")
    df_dem = pd.read_csv(DEMAND_CSV)
    demand = df_dem[["lon", "lat"]].to_numpy(dtype=float)
    weights = df_dem["weight"].to_numpy(dtype=float)
    print(f"  {len(demand):,} demand points, total weight {weights.sum():,.0f}")

    print(f"\nLoading OZP commercial union from {OZP_GEOJSON} ...")
    ozp_gdf = gpd.read_file(OZP_GEOJSON)
    raw_geom = ozp_gdf.iloc[0].geometry
    feasible_geom = raw_geom.buffer(sess12.BUFFER)
    n_pieces = len(feasible_geom.geoms) if hasattr(feasible_geom, "geoms") else 1
    print(f"  Geometry type: {feasible_geom.geom_type}  ({n_pieces} pieces)")
    print(f"  Buffered by {sess12.BUFFER} deg (~10 cm) per Session 010b")

    print(f"\nSweeping k over {K_VALUES} with {N_RESTARTS} restarts each ...")
    summary_rows = []
    all_rows = []
    best_facility_rows = []
    sweep_t0 = time.time()

    for k in K_VALUES:
        print(f"\n--- k = {k} ---")
        rng = np.random.default_rng(RNG_SEED)   # fresh RNG per k
        k_t0 = time.time()
        results = []
        for r in range(1, N_RESTARTS + 1):
            rt0 = time.time()
            res = sess12.lloyd_one_restart(demand, weights, feasible_geom, k, rng, r)
            res["runtime_s"] = time.time() - rt0
            results.append(res)
            print(
                f"  Restart {r:2d}: obj={res['final_obj']:>10,.0f}  "
                f"iters={res['n_lloyd_iters']:>2d}  "
                f"SLSQP={res['slsqp_calls']:>4d}/{res['weiszfeld_calls']:>4d}  "
                f"converged={str(res['converged']):>5s}  "
                f"t={res['runtime_s']:.2f}s"
            )
        k_total_t = time.time() - k_t0

        best = min(results, key=lambda r: r["final_obj"])
        best_obj = best["final_obj"]
        worst_obj = max(r["final_obj"] for r in results)
        gap_pct = 100.0 * (worst_obj - best_obj) / best_obj
        distinct = len({round(r["final_obj"], 0) for r in results})
        n_converged = sum(1 for r in results if r["converged"])
        mean_obj = float(np.mean([r["final_obj"] for r in results]))
        median_obj = float(np.median([r["final_obj"] for r in results]))

        summary_rows.append({
            "k": k,
            "best_obj": best_obj,
            "worst_obj": worst_obj,
            "mean_obj": mean_obj,
            "median_obj": median_obj,
            "worst_best_gap_pct": gap_pct,
            "distinct_local_optima": distinct,
            "n_converged": n_converged,
            "n_restarts": N_RESTARTS,
            "total_runtime_s": k_total_t,
            "pct_of_baseline": 100.0 * best_obj / BASELINE_SINGLE,
            "pct_reduction_vs_baseline": 100.0 * (1.0 - best_obj / BASELINE_SINGLE),
        })
        print(
            f"  k={k} SUMMARY: best={best_obj:,.0f} | worst={worst_obj:,.0f} | "
            f"gap {gap_pct:.1f}% | distinct {distinct} | "
            f"converged {n_converged}/{N_RESTARTS} | t={k_total_t:.1f}s"
        )

        for r in results:
            all_rows.append({
                "k": k,
                "restart_id": r["restart_id"],
                "final_obj": r["final_obj"],
                "n_lloyd_iters": r["n_lloyd_iters"],
                "converged": r["converged"],
                "slsqp_calls": r["slsqp_calls"],
                "weiszfeld_calls": r["weiszfeld_calls"],
                "runtime_s": r["runtime_s"],
            })

        for j, (lon, lat) in enumerate(best["facilities"]):
            best_facility_rows.append({
                "k": k,
                "facility_id": j,
                "lon": lon,
                "lat": lat,
            })

        # crash-safe checkpoint: rewrite all three CSVs after each k completes
        pd.DataFrame(summary_rows).to_csv(OUT_SUMMARY, index=False)
        pd.DataFrame(all_rows).to_csv(OUT_ALL, index=False)
        pd.DataFrame(best_facility_rows).to_csv(OUT_BEST_FAC, index=False)

    total_sweep_t = time.time() - sweep_t0
    print(f"\nTotal sweep runtime: {total_sweep_t:.1f}s ({total_sweep_t/60:.1f} min)")
    print("\nOutputs written to:")
    print(f"  {OUT_SUMMARY}")
    print(f"  {OUT_ALL}")
    print(f"  {OUT_BEST_FAC}")

    print("\nDiminishing returns table:")
    df_sum = pd.DataFrame(summary_rows)
    cols = ["k", "best_obj", "pct_reduction_vs_baseline", "worst_best_gap_pct",
            "distinct_local_optima", "n_converged", "total_runtime_s"]
    print(df_sum[cols].to_string(index=False))

    print("\nDone.")


if __name__ == "__main__":
    main()