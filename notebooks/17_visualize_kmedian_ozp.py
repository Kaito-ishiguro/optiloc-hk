"""
notebooks/17_visualize_kmedian_ozp.py

Session 012: Folium map of the OZP-constrained k=5 k-median network result.

Layers (z-order, bottom to top):
  1. CartoDB Positron base tiles
  2. Demand heatmap (KDE-style)
  3. OZP commercial union (subtle beige overlay — feasible region context)
  4. Voronoi service areas (5 cells, translucent facility colors)
  5. Lloyd convergence trails (dashed, per facility)
  6. Init facility markers (small hollow circles)
  7. Final facility markers (large filled circles, dark border)
  8. Title + legend HTML overlay

Color scheme matches Session 015 (15_visualize_kmedian.py) so the constrained
and unconstrained maps can be visually cross-referenced.
"""

from pathlib import Path
import json

import folium
from folium.plugins import HeatMap
from folium import Element
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPoint
from shapely.ops import voronoi_diagram


DATA_DIR = Path("data/processed")
DEMAND_CSV = DATA_DIR / "demand_points.csv"
OZP_GEOJSON = DATA_DIR / "ozp_commercial_union.geojson"
RESULT_CSV = DATA_DIR / "kmedian_ozp_result.csv"
TRAILS_CSV = DATA_DIR / "kmedian_ozp_trails.csv"

MAPS_DIR = Path("docs/maps")
OUT_HTML = MAPS_DIR / "07_kmedian_ozp_map.html"

# HK bounding box for Voronoi envelope clip
HK_ENVELOPE = Polygon([
    (113.80, 22.15),
    (114.50, 22.15),
    (114.50, 22.60),
    (113.80, 22.60),
])

# Facility colors — matched to Session 015 for visual continuity
COLORS = [
    "#7F77DD",  # F1 purple
    "#1D9E75",  # F2 teal
    "#D85A30",  # F3 coral
    "#378ADD",  # F4 blue
    "#BA7517",  # F5 amber
]

# Human-readable region labels for the Session 012 winning restart positions.
# If a re-run produces a different facility ordering, update these by inspection.
REGION_LABELS = [
    "F1: Northern NT (Tai Po area)",
    "F2: Tsuen Wan / NW NT",
    "F3: Eastern Kowloon (Kwun Tong)",
    "F4: Tuen Mun / western NT",
    "F5: Central Kowloon",
]


def main():
    print("Loading data ...")
    df_dem = pd.read_csv(DEMAND_CSV)
    df_result = pd.read_csv(RESULT_CSV)
    df_trails = pd.read_csv(TRAILS_CSV)
    ozp_gdf = gpd.read_file(OZP_GEOJSON)
    ozp_geom = ozp_gdf.iloc[0].geometry

    facilities = df_result[["lon", "lat"]].to_numpy()
    inits = df_trails[df_trails["iter"] == 0].sort_values("facility_id")[["lon", "lat"]].to_numpy()
    K = len(facilities)
    n_iters = int(df_trails["iter"].max()) + 1
    print(f"  K={K} facilities, {n_iters} trail snapshots recorded")

    # Build Voronoi over the 5 facilities, clipped to HK envelope
    print("Building Voronoi cells ...")
    fac_points = MultiPoint([Point(x, y) for x, y in facilities])
    vor = voronoi_diagram(fac_points, envelope=HK_ENVELOPE)
    voronoi_cells = list(vor.geoms)

    # Match each Voronoi cell to its facility via point-in-polygon containment
    cell_for_fac = [None] * K
    for cell in voronoi_cells:
        for j, (lon, lat) in enumerate(facilities):
            if cell.contains(Point(lon, lat)):
                cell_for_fac[j] = cell
                break
    for j in range(K):
        if cell_for_fac[j] is None:
            print(f"  WARNING: facility F{j+1} not contained in any Voronoi cell")

    # Init the map
    print("Building Folium map ...")
    m = folium.Map(
        location=[22.32, 114.17],
        zoom_start=11,
        tiles="CartoDB Positron",
        control_scale=True,
    )

    # Layer 2: Heatmap
    heat_data = df_dem[["lat", "lon", "weight"]].values.tolist()
    HeatMap(
        heat_data,
        radius=12,
        blur=15,
        min_opacity=0.3,
        max_zoom=13,
    ).add_to(m)

    # Layer 3: OZP commercial union (subtle beige overlay)
    ozp_geojson = json.loads(gpd.GeoSeries([ozp_geom]).to_json())
    folium.GeoJson(
        ozp_geojson,
        name="OZP commercial zones",
        style_function=lambda f: {
            "fillColor": "#D6B36A",
            "color": "#7A5A1A",
            "weight": 0.4,
            "fillOpacity": 0.22,
        },
    ).add_to(m)

    # Layer 4: Voronoi service areas (one per facility)
    for j in range(K):
        cell = cell_for_fac[j]
        if cell is None:
            continue
        # voronoi_diagram + envelope clip can return Polygon or MultiPolygon per cell
        geoms = list(cell.geoms) if cell.geom_type == "MultiPolygon" else [cell]
        color = COLORS[j]
        for g in geoms:
            cell_geojson = json.loads(gpd.GeoSeries([g]).to_json())
            folium.GeoJson(
                cell_geojson,
                style_function=lambda feat, c=color: {
                    "fillColor": c,
                    "color": c,
                    "weight": 1.2,
                    "fillOpacity": 0.16,
                },
            ).add_to(m)

    # Layer 5: Lloyd convergence trails (dashed polylines)
    for j in range(K):
        trail = df_trails[df_trails["facility_id"] == j].sort_values("iter")
        coords = trail[["lat", "lon"]].values.tolist()
        folium.PolyLine(
            coords,
            color=COLORS[j],
            weight=2.5,
            opacity=0.85,
            dash_array="6, 4",
        ).add_to(m)

    # Layer 6: Init markers (small hollow circles)
    for j, (lon, lat) in enumerate(inits):
        folium.CircleMarker(
            location=(lat, lon),
            radius=6,
            color=COLORS[j],
            weight=2,
            fill=False,
            tooltip=f"F{j+1} init: ({lon:.5f}, {lat:.5f})",
        ).add_to(m)

    # Layer 7: Final facility markers (large filled circles with dark border)
    for j, (lon, lat) in enumerate(facilities):
        folium.CircleMarker(
            location=(lat, lon),
            radius=13,
            color="#1A1A1A",
            weight=2,
            fill=True,
            fill_color=COLORS[j],
            fill_opacity=0.95,
            tooltip=f"{REGION_LABELS[j]}: ({lon:.5f}, {lat:.5f})",
        ).add_to(m)

    # Layer 8: Title + Legend overlay
    legend_facility_rows = "".join(
        f"<div style='display:flex;align-items:center;margin:2px 0'>"
        f"<span style='width:14px;height:14px;background:{COLORS[j]};"
        f"border:1.5px solid #1A1A1A;border-radius:50%;margin-right:8px;flex-shrink:0'></span>"
        f"<span>{REGION_LABELS[j]}</span></div>"
        for j in range(K)
    )
    legend_facility_rows += (
        "<div style='display:flex;align-items:center;margin:6px 0 2px 0'>"
        "<span style='width:14px;height:9px;background:#D6B36A;border:1px solid #7A5A1A;"
        "margin-right:8px;flex-shrink:0'></span><span>OZP commercial zones (0.9% of HK land)</span></div>"
    )
    title_html = """
    <div style="position:fixed; top:10px; left:60px; z-index:9999;
                background:rgba(255,255,255,0.94); padding:10px 14px;
                border:1px solid #888; border-radius:6px;
                font-family:sans-serif; font-size:13px; max-width:420px;">
      <div style="font-size:15px; font-weight:600; margin-bottom:4px;">
        OptiLoc HK — k=5 facilities, OZP-constrained
      </div>
      <div style="color:#555;">
        Lloyd's algorithm + Weiszfeld / SLSQP inner solver. Best of 10 restarts.<br>
        Objective: 277,595 weighted-units &nbsp;(+1.0% vs unconstrained 274,830).
      </div>
    </div>
    """
    legend_html = f"""
    <div style="position:fixed; bottom:30px; left:30px; z-index:9999;
                background:rgba(255,255,255,0.94); padding:10px 14px;
                border:1px solid #888; border-radius:6px;
                font-family:sans-serif; font-size:12px;">
      <div style="font-weight:600; margin-bottom:6px;">Facilities &amp; service areas</div>
      {legend_facility_rows}
    </div>
    """
    m.get_root().html.add_child(Element(title_html))
    m.get_root().html.add_child(Element(legend_html))

    # Save
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    m.save(str(OUT_HTML))
    print(f"\nSaved {OUT_HTML}")
    print("\nNext: open the HTML in a browser, then take two screenshots with")
    print("Snipping Tool (Win+Shift+S) and save them as:")
    print("  - docs/maps/kmedian_ozp_map_wide.png   (entire HK, all 5 facilities + commercial overlay)")
    print("  - docs/maps/kmedian_ozp_map_zoom.png   (zoom on Kowloon corridor; F3 + F5)")


if __name__ == "__main__":
    main()
