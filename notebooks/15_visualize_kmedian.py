"""
15_visualize_kmedian.py — Multi-facility k-median Voronoi map.

Reads kmedian_result.csv + kmedian_trails.csv, renders a Folium map with:
  - HK population heatmap
  - 5 Voronoi service-area polygons (translucent, color-coded)
  - Convergence trails of each facility from init to final position
  - 5 init markers (hollow) + 5 final facility markers (filled)
"""

from pathlib import Path

import folium
import pandas as pd
from folium.plugins import HeatMap
from shapely.geometry import MultiPoint, Point, Polygon
from shapely.ops import voronoi_diagram

DATA = Path(__file__).resolve().parent.parent / "data" / "processed"
MAPS = Path(__file__).resolve().parent.parent / "docs" / "maps"
MAPS.mkdir(parents=True, exist_ok=True)

# --- load ---
print("Loading data ...")
demand = pd.read_csv(DATA / "demand_points.csv")
result = pd.read_csv(DATA / "kmedian_result.csv")
trails = pd.read_csv(DATA / "kmedian_trails.csv")
print(f"  {len(demand):,} demand points, {len(result)} facilities, {len(trails)} trail rows")

facilities = result[["lon", "lat"]].values
K = len(facilities)

# distinct colors for the 5 service areas
COLORS = ["#7F77DD", "#1D9E75", "#D85A30", "#378ADD", "#BA7517"]

# --- Voronoi cells, clipped to HK bbox ---
print("Computing Voronoi cells ...")
hk_bbox = Polygon([(113.80, 22.15), (114.50, 22.15), (114.50, 22.60), (113.80, 22.60)])
facility_pts = MultiPoint([(x, y) for x, y in facilities])
vor = voronoi_diagram(facility_pts, envelope=hk_bbox)

# match each output polygon to its facility by containment test
cell_for_facility = {}
for poly in vor.geoms:
    poly_clipped = poly.intersection(hk_bbox)
    for j, f in enumerate(facilities):
        if poly.contains(Point(f[0], f[1])):
            cell_for_facility[j] = poly_clipped
            break
print(f"  Matched {len(cell_for_facility)}/{K} cells to facilities")

# --- build map ---
print("Building Folium map ...")
m = folium.Map(location=[22.36, 114.13], zoom_start=11, tiles="CartoDB positron")

# heatmap (background)
HeatMap(
    demand[["lat", "lon", "weight"]].values.tolist(),
    radius=8,
    blur=10,
    min_opacity=0.3,
).add_to(m)

# Voronoi service-area polygons (translucent fills)
for j, cell in cell_for_facility.items():
    color = COLORS[j]
    geoms = [cell] if cell.geom_type == "Polygon" else list(cell.geoms)
    for g in geoms:
        if g.is_empty:
            continue
        coords = [[lat, lon] for lon, lat in g.exterior.coords]
        folium.Polygon(
            locations=coords,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.18,
            popup=f"Service area F{j+1}",
        ).add_to(m)

# convergence trails (dashed polyline per facility)
for j in range(K):
    trail = trails[trails["facility_id"] == j].sort_values("iter")
    coords = [[r["lat"], r["lon"]] for _, r in trail.iterrows()]
    folium.PolyLine(
        locations=coords,
        color=COLORS[j],
        weight=2.5,
        opacity=0.75,
        dash_array="6, 4",
        popup=f"F{j+1} Lloyd convergence trail ({len(coords)} positions)",
    ).add_to(m)

# init markers (small hollow circles)
for j in range(K):
    init = trails[(trails["facility_id"] == j) & (trails["iter"] == 0)].iloc[0]
    folium.CircleMarker(
        location=[init["lat"], init["lon"]],
        radius=6,
        color=COLORS[j],
        fill=False,
        weight=2,
        opacity=0.7,
        popup=f"F{j+1} init position",
    ).add_to(m)

# final facility markers (large filled circles, on top)
for j in range(K):
    lon, lat = facilities[j]
    folium.CircleMarker(
        location=[lat, lon],
        radius=13,
        color="#222222",
        fill=True,
        fill_color=COLORS[j],
        fill_opacity=0.95,
        weight=2.5,
        popup=f"<b>Facility F{j+1}</b><br>lon: {lon:.5f}<br>lat: {lat:.5f}",
    ).add_to(m)

# title overlay
title_html = """
<div style="position: fixed; top: 10px; left: 50px; z-index: 9999;
            background: white; padding: 10px 16px; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15); font-family: sans-serif;">
  <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">
    OptiLoc HK &mdash; k=5 facility network
  </div>
  <div style="font-size: 12px; color: #555;">
    Lloyd's algorithm + Weiszfeld inner solver &middot; objective 274,830 &middot; 59.1% reduction vs single facility
  </div>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# legend
legend_html = (
    '<div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; '
    'background: white; padding: 10px 14px; border-radius: 8px; '
    'box-shadow: 0 2px 8px rgba(0,0,0,0.15); font-family: sans-serif; font-size: 12px;">'
    '<div style="font-weight: 600; margin-bottom: 6px;">Legend</div>'
)
for j in range(K):
    legend_html += (
        f'<div style="display: flex; align-items: center; gap: 6px; margin: 2px 0;">'
        f'<div style="width: 14px; height: 14px; background: {COLORS[j]}; '
        f'border: 2px solid #222; border-radius: 50%;"></div>'
        f'<span>F{j+1} (filled circle) &amp; service area</span></div>'
    )
legend_html += (
    '<div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #eee;">'
    '<span style="display: inline-block; width: 18px; border-top: 2px dashed #555; '
    'margin-right: 6px; vertical-align: middle;"></span>Lloyd convergence trail</div>'
    '<div style="margin-top: 4px;">'
    '<span style="display: inline-block; width: 12px; height: 12px; '
    'border: 2px solid #555; border-radius: 50%; margin-right: 6px; vertical-align: middle;">'
    '</span>random init position</div>'
    '</div>'
)
m.get_root().html.add_child(folium.Element(legend_html))

out = MAPS / "06_kmedian_map.html"
m.save(str(out))
print(f"\nSaved map to {out}")
print(f"Open with: start {out}")