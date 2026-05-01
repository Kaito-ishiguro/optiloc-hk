"""
OptiLoc HK — Session 005b: visualize the constrained optimum

Renders a single Folium map showing:
  - Population heatmap (background context)
  - Kowloon district polygon (green, the location constraint)
  - MTR exits with 500m proximity circles (purple)
  - Competitor exclusion zones, 200m radius (red)
  - Unconstrained optimum (gold star, Mong Kok from Session 003)
  - Constrained optimum (red star, jumped to satisfy constraints)
  - Title + legend baked into HTML

Output: docs/maps/03_constrained_map.html

Run from repo root:
    python notebooks/06_visualize_constrained.py
"""

from pathlib import Path

import folium
import pandas as pd
import osmnx as ox
from folium.plugins import HeatMap

# ---------- Paths ----------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
MAPS_DIR = REPO_ROOT / "docs" / "maps"
MAPS_DIR.mkdir(parents=True, exist_ok=True)

DEMAND_CSV = DATA_PROCESSED / "demand_points.csv"
RESULT_CSV = DATA_PROCESSED / "constrained_result.csv"
CONSTRAINTS_CSV = DATA_PROCESSED / "constraints_geo.csv"
OUTPUT_HTML = MAPS_DIR / "03_constrained_map.html"

# ---------- Config ----------
M_PER_DEG = 107_000
MTR_RADIUS_M = 500
COMPETITOR_RADIUS_M = 200
UNCONSTRAINED_OPT = (114.17071, 22.33729)  # from Session 003

# ---------- Load ----------
demand = pd.read_csv(DEMAND_CSV)
result = pd.read_csv(RESULT_CSV).iloc[0]
geo = pd.read_csv(CONSTRAINTS_CSV)
mtr = geo[geo["kind"] == "mtr"]
competitors = geo[geo["kind"] == "competitor"]

print(f"Constrained optimum: ({result['lon_opt']:.5f}, {result['lat_opt']:.5f})")
print(f"Unconstrained optimum (Session 003): {UNCONSTRAINED_OPT}")

# Distance the optimum jumped due to constraints (rough degree -> m)
import math
dlon = result['lon_opt'] - UNCONSTRAINED_OPT[0]
dlat = result['lat_opt'] - UNCONSTRAINED_OPT[1]
jump_m = math.sqrt(dlon**2 + dlat**2) * M_PER_DEG
print(f"Optimum jumped {jump_m:.0f} m due to constraints")

# ---------- Build map ----------
m = folium.Map(
    location=[22.33, 114.17],
    zoom_start=13,
    tiles="cartodbpositron",
)

# Layer 1: Population heatmap
heat_data = demand[["lat", "lon", "weight"]].values.tolist()
HeatMap(heat_data, radius=8, blur=12, min_opacity=0.2, max_zoom=14,
        name="Population").add_to(m)

# Layer 2: Kowloon polygon
print("Fetching Kowloon polygon for visualization...")
kowloon_gdf = ox.geocode_to_gdf("Kowloon, Hong Kong")
folium.GeoJson(
    kowloon_gdf.geometry.iloc[0].__geo_interface__,
    style_function=lambda _: {
        "fillColor": "#1D9E75",
        "color": "#0F6E56",
        "weight": 2,
        "fillOpacity": 0.08,
    },
    name="Kowloon district (constraint 1)",
    tooltip="Constraint 1: must lie within Kowloon",
).add_to(m)

# Layer 3: MTR proximity zones (500m circles, union forms the feasible region for constraint 2)
mtr_layer = folium.FeatureGroup(name="MTR exits + 500m zones (constraint 2)")
for _, row in mtr.iterrows():
    folium.Circle(
        location=[row["lat"], row["lon"]],
        radius=MTR_RADIUS_M,
        color="#534AB7",
        weight=0.5,
        fill=True,
        fill_color="#534AB7",
        fill_opacity=0.04,
    ).add_to(mtr_layer)
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=2,
        color="#3C3489",
        fill=True,
        fill_color="#3C3489",
        fill_opacity=1,
    ).add_to(mtr_layer)
mtr_layer.add_to(m)

# Layer 4: Competitor exclusion zones (200m circles - facility must NOT be inside)
comp_layer = folium.FeatureGroup(name="Competitor exclusion zones (constraint 3)")
for _, row in competitors.iterrows():
    folium.Circle(
        location=[row["lat"], row["lon"]],
        radius=COMPETITOR_RADIUS_M,
        color="#A32D2D",
        weight=2,
        fill=True,
        fill_color="#E24B4A",
        fill_opacity=0.18,
        dash_array="6,6",
    ).add_to(comp_layer)
    folium.Marker(
        location=[row["lat"], row["lon"]],
        icon=folium.Icon(color="red", icon="ban", prefix="fa"),
        popup=f"Competitor {int(row['id']) + 1}",
    ).add_to(comp_layer)
comp_layer.add_to(m)

# Layer 5: Unconstrained optimum (gold star, dimmed)
folium.CircleMarker(
    location=[UNCONSTRAINED_OPT[1], UNCONSTRAINED_OPT[0]],
    radius=12,
    color="#1A1A1A",
    weight=2,
    fill=True,
    fill_color="#FFD60A",
    fill_opacity=0.7,
    popup=f"<b>Unconstrained optimum (Session 003)</b><br>"
          f"({UNCONSTRAINED_OPT[0]:.5f}, {UNCONSTRAINED_OPT[1]:.5f})<br>"
          f"<i>Mong Kok / Prince Edward MTR</i>",
).add_to(m)

# Layer 6: Constrained optimum (red star)
folium.Marker(
    location=[result["lat_opt"], result["lon_opt"]],
    icon=folium.Icon(color="red", icon="star", prefix="fa"),
    popup=(
        f"<b>Constrained optimum</b><br>"
        f"({result['lon_opt']:.5f}, {result['lat_opt']:.5f})<br>"
        f"f(x*) = {result['f_opt']:,.0f}<br>"
        f"Jumped {jump_m:.0f} m from unconstrained answer"
    ),
).add_to(m)
folium.CircleMarker(
    location=[result["lat_opt"], result["lon_opt"]],
    radius=14,
    color="#1A1A1A",
    weight=3,
    fill=True,
    fill_color="#E63946",
    fill_opacity=0.95,
).add_to(m)

# Layer 7: A line connecting the two optima to show the "jump"
folium.PolyLine(
    locations=[
        [UNCONSTRAINED_OPT[1], UNCONSTRAINED_OPT[0]],
        [result["lat_opt"], result["lon_opt"]],
    ],
    color="#1A1A1A",
    weight=2,
    opacity=0.6,
    dash_array="8,8",
).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

# Title + legend overlays
title_html = """
<div style="position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
            background: white; padding: 10px 18px; border: 2px solid #1A1A1A;
            border-radius: 6px; font-family: -apple-system, sans-serif;
            font-size: 16px; font-weight: 600; z-index: 9999;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
    OptiLoc HK — KKT-constrained facility location
</div>
"""

legend_html = f"""
<div style="position: fixed; bottom: 24px; left: 24px;
            background: white; padding: 14px 16px; border: 2px solid #1A1A1A;
            border-radius: 6px; font-family: -apple-system, sans-serif;
            font-size: 12px; line-height: 1.6; z-index: 9999;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15); max-width: 300px;">
    <div style="font-weight: 600; font-size: 13px; margin-bottom: 6px;">
        Constraints (all signed-distance functions)
    </div>
    <div style="margin-bottom: 4px;">
        <span style="display: inline-block; width: 14px; height: 14px;
                     background: #1D9E75; opacity: 0.4;
                     vertical-align: middle; margin-right: 6px;"></span>
        Must lie within <b>Kowloon</b>
    </div>
    <div style="margin-bottom: 4px;">
        <span style="display: inline-block; width: 14px; height: 14px;
                     border-radius: 50%; background: #534AB7; opacity: 0.4;
                     vertical-align: middle; margin-right: 6px;"></span>
        Within <b>500m of an MTR exit</b>
    </div>
    <div style="margin-bottom: 8px;">
        <span style="display: inline-block; width: 14px; height: 14px;
                     border-radius: 50%; background: #E24B4A; opacity: 0.4;
                     vertical-align: middle; margin-right: 6px;
                     border: 2px dashed #A32D2D;"></span>
        At least <b>200m from competitors</b>
    </div>
    <div style="font-weight: 600; font-size: 13px; margin: 8px 0 4px;">
        Optima
    </div>
    <div style="margin-bottom: 4px;">
        <span style="color: #B8860B; font-size: 14px;">●</span>
        Unconstrained: Mong Kok ({UNCONSTRAINED_OPT[0]:.4f}, {UNCONSTRAINED_OPT[1]:.4f})
    </div>
    <div>
        <span style="color: #E63946; font-size: 14px;">★</span>
        <b>Constrained: ({result['lon_opt']:.4f}, {result['lat_opt']:.4f})</b><br>
        <span style="font-size: 11px; color: #555;">
            jumped {jump_m:.0f} m to satisfy constraints
        </span>
    </div>
</div>
"""

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

m.save(str(OUTPUT_HTML))
print(f"\nSaved -> {OUTPUT_HTML}")
print(f"Open it: file://{OUTPUT_HTML.resolve()}")
