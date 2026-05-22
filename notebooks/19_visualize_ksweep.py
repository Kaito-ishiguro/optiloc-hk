"""
notebooks/19_visualize_ksweep.py

Session 013: visualize k-sweep diminishing returns.

Reads:
  data/processed/ksweep_ozp_summary.csv      (one row per k)
  data/processed/ksweep_ozp_all_restarts.csv (one row per restart)

Produces a two-panel landing-page chart:
  Top:    best objective vs k with multi-start min-max band and
          per-point % reduction vs single-facility Weber baseline.
  Bottom: worst-best gap (%) vs k, with Lloyd convergence rate
          annotated above each bar.

Saves a single high-DPI PNG to docs/maps/.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path("data/processed")
OUT_DIR = Path("docs/maps")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_CSV = DATA_DIR / "ksweep_ozp_summary.csv"
ALL_CSV = DATA_DIR / "ksweep_ozp_all_restarts.csv"
OUT_PNG = OUT_DIR / "08_ksweep_diminishing_returns.png"

BASELINE = 671_466.0   # Session 003 single-facility Weber objective


def main():
    print(f"Loading {SUMMARY_CSV} ...")
    summ = pd.read_csv(SUMMARY_CSV).sort_values("k").reset_index(drop=True)
    print(summ.to_string(index=False))

    ks = summ["k"].to_numpy()
    best = summ["best_obj"].to_numpy() / 1000.0
    worst = summ["worst_obj"].to_numpy() / 1000.0
    median = summ["median_obj"].to_numpy() / 1000.0
    gap = summ["worst_best_gap_pct"].to_numpy()
    pct_red = summ["pct_reduction_vs_baseline"].to_numpy()
    n_conv = summ["n_converged"].to_numpy()
    n_restarts = summ["n_restarts"].to_numpy()

    NAVY = "#1f3a5f"
    BAND = "#a9c3e0"
    GRAY = "#888888"
    PURPLE = "#7a3b8f"

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 9),
        gridspec_kw={"height_ratios": [2.0, 1.0]},
        sharex=True,
    )
    fig.patch.set_facecolor("white")

    # ---------- top panel: objective vs k ----------
    ax1.fill_between(
        ks, best, worst, color=BAND, alpha=0.5,
        label=f"multi-start min-max ({n_restarts[0]} restarts)",
    )
    ax1.plot(
        ks, median, color=GRAY, linestyle=":", linewidth=1.2,
        label="median across restarts",
    )
    ax1.plot(
        ks, best, color=NAVY, marker="o", markersize=8, linewidth=2.2,
        label="best objective (multi-start min)",
    )

    # single-facility baseline reference
    ax1.axhline(BASELINE / 1000.0, color=GRAY, linestyle="--", linewidth=1, alpha=0.6)
    ax1.text(
        ks[0], BASELINE / 1000.0 + 8,
        f"single-facility Weber baseline ({BASELINE/1000:.0f}k weighted-units)",
        color=GRAY, fontsize=9, va="bottom", ha="left", style="italic",
    )

    # % reduction labels under each best-marker
    for k, b, p in zip(ks, best, pct_red):
        ax1.annotate(
            f"−{p:.0f}%",
            xy=(k, b),
            xytext=(0, -16),
            textcoords="offset points",
            fontsize=9.5, color=NAVY, ha="center", va="top", fontweight="bold",
        )

    ax1.set_ylabel("total weighted distance\n(thousands of weighted-units)", fontsize=11)
    ax1.set_title(
        "How many hubs is enough for Hong Kong?\n"
        "OZP-constrained k-median objective vs number of facilities",
        fontsize=13, pad=12,
    )
    ax1.legend(loc="upper right", framealpha=0.95, fontsize=9)
    ax1.grid(True, alpha=0.25)
    ax1.set_ylim(0, BASELINE / 1000.0 * 1.08)

    # ---------- bottom panel: multi-start gap + convergence ----------
    ax2.bar(
        ks, gap, width=1.2, color=PURPLE, alpha=0.55,
        edgecolor=PURPLE, linewidth=1.0, label="worst-best gap (%)",
    )
    for k, g, nc, nr in zip(ks, gap, n_conv, n_restarts):
        ax2.text(
            k, g + 1.0, f"{nc}/{nr} converged",
            ha="center", va="bottom", fontsize=8.5, color="#444",
        )

    ax2.set_xlabel("number of facilities, k", fontsize=11)
    ax2.set_ylabel("worst-best gap (%)\nmulti-start variance", fontsize=10)
    ax2.set_title(
        "Non-convexity worsens with k  ·  Lloyd convergence rate annotated above bars",
        fontsize=10.5, pad=8,
    )
    ax2.set_xticks(ks)
    ax2.grid(True, axis="y", alpha=0.25)
    ax2.set_ylim(0, max(gap) * 1.30)

    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=180, facecolor="white", bbox_inches="tight")
    print(f"\nSaved: {OUT_PNG}")


if __name__ == "__main__":
    main()