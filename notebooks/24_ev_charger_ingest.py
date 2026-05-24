import requests
import geopandas as gpd
from shapely.geometry import Point
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_URL = (
    "https://portal.csdi.gov.hk/server/services/common/"
    "epd_rcd_1631080339740_69941/MapServer/WFSServer"
)

# --- Fetch all features ---
r = requests.get(BASE_URL, params={
    "service": "WFS",
    "version": "2.0.0",
    "request": "GetFeature",
    "typeName": "csdi:geotagging",
    "outputFormat": "GeoJSON",
    "srsName": "EPSG:4326"
}, timeout=60)

data = r.json()
print(f"Total charger locations: {len(data['features'])}")

# --- Build GeoDataFrame ---
gdf = gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4326")
print(f"Columns: {list(gdf.columns)}")
print(gdf.head(3))

# --- Compute totals ---
charger_cols = [c for c in gdf.columns if c.endswith("_no")]
gdf["total_chargers"] = gdf[charger_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)
print(f"\nTotal charger points (connectors): {int(gdf['total_chargers'].sum())}")

# --- District summary ---
district_summary = (
    gdf.groupby("NAME_OF_DISTRICT_COUNCIL_DISTRICT_EN")["total_chargers"]
    .sum()
    .sort_values(ascending=False)
)
print("\nChargers by district:")
print(district_summary.to_string())

# --- Save GeoJSON ---
out_path = Path("data/processed/ev_chargers.geojson")
gdf.to_file(out_path, driver="GeoJSON")
print(f"\nSaved: {out_path}  ({len(gdf)} locations)")

# --- Map ---
fig, ax = plt.subplots(figsize=(10, 12))
gdf.plot(ax=ax, markersize=3, color="teal", alpha=0.6)
ax.set_title("HK Public EV Charger Locations (906 sites)", fontsize=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_facecolor("#0d1117")
fig.patch.set_facecolor("#0d1117")
ax.title.set_color("white")
ax.xaxis.label.set_color("white")
ax.yaxis.label.set_color("white")
ax.tick_params(colors="white")
plt.tight_layout()
plt.savefig("docs/maps/24_ev_chargers.png", dpi=150, bbox_inches="tight")
print("Map saved: docs/maps/24_ev_chargers.png")
plt.show()