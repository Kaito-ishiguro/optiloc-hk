"""
OptiLoc HK — Session 004b: convergence visualization

Renders the final shareable map showing:
  - HK population heatmap as background context
  - 4 starting points (color-coded by location)
  - For each starting point: gradient descent trail (thin polyline)
                             Newton-Raphson trail (thick polyline)
  - The shared optimum at Prince Edward MTR
  - A legend explaining the visual encoding

Output: docs/maps/02_convergence_map.html — a self-contained HTML file
suitable for screenshotting and sharing on LinkedIn / Twitter.

Run from repo root:
    python notebooks/04_visualize_convergence.py
"""

from pathlib import Path

import folium
import pandas as pd
from folium.plugins import HeatMap

# ---------- Paths ----------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
MAPS_DIR = REPO_ROOT / "docs" / "maps"
MAPS_DIR.mkdir(parents=True, exist_ok=True)

DEMAND_CSV = DATA_PROCESSED / "demand_points.csv"
TRAILS_CSV = DATA_PROCESSED / "trails_multistart.csv"
OUTPUT_HTML = MAPS_DIR / "02_convergence_map.html"

# ---------- Load data ----------
demand = pd.read_csv(DEMAND_CSV)
trails = pd.read_csv(TRAILS_CSV)
print(f"Loaded {len(demand):,} demand points and {len(trails):,} trail points")

# ---------- Identify the shared optimum ----------
# All 8 trails converge to ~the same point; take Newton-Raphson's final
# point from any starting point as the canonical optimum.
optimum_row = trails[trails["method"] == "Newton-Raphson"].groupby("start_name").last().iloc[0]
OPT_LON, OPT_LAT = optimum_row["lon"], optimum_row["lat"]
print(f"Shared optimum: ({OPT_LON:.5f}, {OPT_LAT:.5f}) — Prince Edward MTR / Mong Kok")

# ---------- Build the map ----------
HK_CENTER = [22.36, 114.13]
m = folium.Map(
    location=HK_CENTER,
    zoom_start=11,
    tiles="cartodbpositron",
)

# Layer 1: Population heatmap (background context, low opacity)
heat_data = demand[["lat", "lon", "weight"]].values.tolist()
HeatMap(
    heat_data,
    radius=8,
    blur=12,
    min_opacity=0.2,
    max_zoom=13,
    name="Population density",
).add_to(m)

# Layer 2: Convergence trails — one per (starting point × method)
for (start_name, method), group in trails.groupby(["start_name", "method"]):
    group = group.sort_values("iter")
    color = group["color"].iloc[0]
    coords = list(zip(group["lat"], group["lon"]))
    n_iters = len(group) - 1

    if method == "Gradient Descent":
        weight = 2
        opacity = 0.55
        dash = "5, 5"
    else:  # Newton-Raphson
        weight = 4
        opacity = 0.95
        dash = None

    folium.PolyLine(
        locations=coords,
        color=color,
        weight=weight,
        opacity=opacity,
        dash_array=dash,
        popup=f"{start_name} → {method} ({n_iters} iterations)",
    ).add_to(m)

# Layer 3: Starting point markers
start_points = trails.groupby("start_name").first().reset_index()
for _, row in start_points.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=f"<b>Start: {row['start_name']}</b>",
        icon=folium.Icon(color="lightgray", icon="play", prefix="fa"),
    ).add_to(m)
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=8,
        color=row["color"],
        fill=True,
        fill_color=row["color"],
        fill_opacity=0.9,
        weight=2,
    ).add_to(m)

# Layer 4: The shared optimum
folium.Marker(
    location=[OPT_LAT, OPT_LON],
    popup=(
        f"<b>Optimal facility location</b><br>"
        f"({OPT_LON:.5f}, {OPT_LAT:.5f})<br>"
        f"Prince Edward MTR / Mong Kok<br>"
        f"<i>All 8 trails converge here</i>"
    ),
    icon=folium.Icon(color="red", icon="star", prefix="fa"),
).add_to(m)

folium.CircleMarker(
    location=[OPT_LAT, OPT_LON],
    radius=14,
    color="#1A1A1A",
    weight=3,
    fill=True,
    fill_color="#FFD60A",
    fill_opacity=0.9,
).add_to(m)

# Layer 5: Title and legend overlays (HTML, baked into the map)
title_html = """
<div style="position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
            background: white; padding: 10px 18px; border: 2px solid #1A1A1A;
            border-radius: 6px; font-family: -apple-system, sans-serif;
            font-size: 16px; font-weight: 600; z-index: 9999;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
    OptiLoc HK — Weber Facility Location across 7.5M residents
</div>
"""

legend_html = f"""
<div style="position: fixed; bottom: 24px; left: 24px;
            background: white; padding: 14px 16px; border: 2px solid #1A1A1A;
            border-radius: 6px; font-family: -apple-system, sans-serif;
            font-size: 12px; line-height: 1.5; z-index: 9999;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15); max-width: 280px;">
    <div style="font-weight: 600; font-size: 13px; margin-bottom: 6px;">
        Convergence trails
    </div>
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
        <svg width="40" height="6"><line x1="0" y1="3" x2="40" y2="3"
            stroke="#1A1A1A" stroke-width="4"/></svg>
        <span><b>Newton–Raphson</b> — 4–6 iterations</span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
        <svg width="40" height="6"><line x1="0" y1="3" x2="40" y2="3"
            stroke="#1A1A1A" stroke-width="2" stroke-dasharray="5,5"/></svg>
        <span><b>Gradient descent</b> — 100–300 iterations</span>
    </div>
    <div style="font-weight: 600; font-size: 13px; margin-bottom: 4px;">
        Starting points
    </div>
    <div style="font-size: 11px; color: #555;">
        Tung Chung &middot; Stanley &middot; Sai Kung &middot; Lok Ma Chau
    </div>
    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #ddd;
                font-size: 11px;">
        <span style="color: #B8860B;">★</span>
        Optimum: <b>Prince Edward MTR</b><br>
        ({OPT_LON:.4f}, {OPT_LAT:.4f})
    </div>
</div>
"""

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

# ---------- Save ----------
m.save(str(OUTPUT_HTML))
print(f"\nSaved -> {OUTPUT_HTML}")
print(f"Open it: file://{OUTPUT_HTML.resolve()}")
print("\nThis is the screenshot artifact for LinkedIn / Twitter / your CV.")
