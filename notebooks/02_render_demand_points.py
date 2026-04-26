"""
OptiLoc HK — Session 002b: render demand_points.csv on a Folium map

Reads the demand_points.csv produced by 01_ingest_worldpop.py
and renders an interactive HK map showing the population distribution.

For ~10,000+ WorldPop cells, individual CircleMarkers are too slow,
so we use Folium's HeatMap layer plus a sample of the heaviest cells
as visible markers for sanity checking.

Run from repo root:
    python notebooks/02_render_demand_points.py
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

INPUT_FILE = DATA_PROCESSED / "demand_points.csv"
OUTPUT_FILE = MAPS_DIR / "01_first_map.html"

# ---------- Load ----------
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT_FILE}. "
        "Run 01_ingest_worldpop.py first."
    )

df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df):,} demand points (total population: {df['weight'].sum():,.0f})")

# ---------- Build the map ----------
HK_CENTER = [22.3193, 114.1694]   # roughly Victoria Harbour
m = folium.Map(
    location=HK_CENTER,
    zoom_start=11,
    tiles="cartodbpositron",
)

# Heatmap of every populated cell (fast, smooth visual)
heat_data = df[["lat", "lon", "weight"]].values.tolist()
HeatMap(
    heat_data,
    radius=8,
    blur=12,
    min_opacity=0.3,
    max_zoom=13,
    name="Population heatmap",
).add_to(m)

# Top-N heaviest cells as visible markers — sanity check that the data
# lights up where you'd expect (Mong Kok, Sham Shui Po, Kwun Tong, etc.)
TOP_N = 50
top = df.nlargest(TOP_N, "weight")
for _, row in top.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=5,
        popup=f"Population in this 100m cell: {row['weight']:.0f}",
        color="#2c3e50",
        fill=True,
        fill_color="#2c3e50",
        fill_opacity=0.8,
        weight=1,
    ).add_to(m)

folium.LayerControl().add_to(m)

# ---------- Save ----------
m.save(str(OUTPUT_FILE))
print(f"\nSaved map -> {OUTPUT_FILE}")
print(f"Open it: file://{OUTPUT_FILE.resolve()}")
print(f"\nThe heatmap shows the full population distribution.")
print(f"The {TOP_N} dark dots are the most populated 100m cells in HK.")
