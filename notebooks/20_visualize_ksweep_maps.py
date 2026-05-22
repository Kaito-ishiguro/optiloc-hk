"""
notebooks/20_visualize_ksweep_maps.py

Session 013 (continued): 2x3 panel gallery of hub locations across k values.

Reads:
  data/processed/demand_points.csv               (HK demand grid, 41k cells)
  data/processed/ozp_commercial_union.geojson    (feasible C+CDA union)
  data/processed/ksweep_ozp_best_facilities.csv  (best facilities at each k)
  data/processed/ksweep_ozp_summary.csv          (per-k objective for titles)

Renders, for each k in {3, 5, 8, 10, 15, 20}, a panel showing:
  - subtle demand density background (Greys hexbin, weighted)
  - OZP commercial union overlay (beige translucent)
  - Voronoi service areas (one color per facility, translucent)
  - facility markers (navy dots with white edges)

Pairs with notebooks/19_visualize_ksweep.py as the spatial dual of the
diminishing-returns chart: "where the hubs go at each candidate scale."
"""

from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, MultiPoint, box
from shapely.ops import voronoi_diagram

DATA_DIR = Path("data/processed")
OUT_DIR = Path("docs/maps")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DEMAND_CSV = DATA_DIR / "demand_points.csv"
OZP_GEOJSON = DATA_DIR / "ozp_commercial_union.geojson"
BEST_FAC_CSV = DATA_DIR / "ksweep_ozp_best_facilities.csv"
SUMMARY_CSV = DATA_DIR / "ksweep_ozp_summary.csv"
OUT_PNG = OUT_DIR / "09_ksweep_hub_locations.png"

# HK bounding box: covers HK Island + Kowloon + NT + outer islands
HK_BBOX = (113.82, 22.15, 114.45, 22.58)


def compute_voronoi_cells(facilities_xy, bbox):
    """
    facilities_xy: (k, 2) array of (lon, lat).
    Returns a list of k shapely polygons ordered to match facilities_xy
    (matched by point-in-polygon containment).
    """
    pts = MultiPoint([tuple(xy) for xy in facilities_xy])
    envelope = box(*bbox)
    raw = voronoi_diagram(pts, envelope=envelope)
    cells = [None] * len(facilities_xy)
    for cell in raw.geoms:
        clipped = cell.intersection(envelope)
        if clipped.is_empty:
            continue
        for j, xy in enumerate(facilities_xy):
            if clipped.contains(Point(xy)):
                cells[j] = clipped
                break
    return cells


def render_panel(ax, k, facilities_xy, objective, pct_red,
                 demand_lon, demand_lat, demand_w, ozp_gdf):
    # 1) demand background (weighted hexbin, log-binned, subtle)
    ax.hexbin(
        demand_lon, demand_lat, C=demand_w,
        gridsize=80, reduce_C_function=np.sum,
        cmap="Greys", bins="log", mincnt=1, alpha=0.55,
        linewidths=0,
    )

    # 2) OZP commercial union (subtle beige overlay)
    ozp_gdf.plot(ax=ax, color="#D6B36A", edgecolor="none", alpha=0.22)

    # 3) Voronoi cells, one color per facility
    cells = compute_voronoi_cells(facilities_xy, HK_BBOX)
    palette = plt.get_cmap("tab20", 20)
    for j, cell in enumerate(cells):
        if cell is None or cell.is_empty:
            continue
        polys = cell.geoms if hasattr(cell, "geoms") else [cell]
        color = palette(j % 20)
        for p in polys:
            xs, ys = p.exterior.xy
            ax.fill(xs, ys, color=color, alpha=0.28,
                    edgecolor=color, linewidth=0.6)

    # 4) facility markers
    ax.scatter(
        facilities_xy[:, 0], facilities_xy[:, 1],
        s=70, c="#1f3a5f", edgecolor="white", linewidth=1.4,
        zorder=10,
    )

    # frame
    ax.set_xlim(HK_BBOX[0], HK_BBOX[2])
    ax.set_ylim(HK_BBOX[1], HK_BBOX[3])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#cccccc")
    ax.set_title(
        f"k = {k}    obj {objective/1000:.0f}k    −{pct_red:.0f}% vs single-hub",
        fontsize=11, pad=6,
    )


def main():
    print(f"Loading {DEMAND_CSV} ...")
    df_dem = pd.read_csv(DEMAND_CSV)
    demand_lon = df_dem["lon"].to_numpy()
    demand_lat = df_dem["lat"].to_numpy()
    demand_w = df_dem["weight"].to_numpy()
    print(f"  {len(df_dem):,} demand cells")

    print(f"Loading {OZP_GEOJSON} ...")
    ozp_gdf = gpd.read_file(OZP_GEOJSON)

    print(f"Loading {BEST_FAC_CSV} and {SUMMARY_CSV} ...")
    best_fac = pd.read_csv(BEST_FAC_CSV)
    summ = pd.read_csv(SUMMARY_CSV).sort_values("k").reset_index(drop=True)
    summ_by_k = {int(row["k"]): row for _, row in summ.iterrows()}

    k_values = sorted(int(k) for k in best_fac["k"].unique())
    print(f"  k values: {k_values}")

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.patch.set_facecolor("white")

    for ax, k in zip(axes.flat, k_values):
        sub = best_fac[best_fac["k"] == k]
        facilities_xy = sub[["lon", "lat"]].to_numpy()
        row = summ_by_k[k]
        print(f"  rendering panel k={k} ({len(facilities_xy)} hubs) ...")
        render_panel(
            ax, k, facilities_xy,
            objective=row["best_obj"],
            pct_red=row["pct_reduction_vs_baseline"],
            demand_lon=demand_lon, demand_lat=demand_lat,
            demand_w=demand_w, ozp_gdf=ozp_gdf,
        )

    fig.suptitle(
        "Where the hubs land — best OZP-constrained k-median network at each scale\n"
        "demand heatmap (gray)  ·  commercial zones (beige)  ·  Voronoi service areas (color)  ·  facilities (navy)",
        fontsize=14, y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_PNG, dpi=160, facecolor="white", bbox_inches="tight")
    print(f"\nSaved: {OUT_PNG}")


if __name__ == "__main__":
    main()