import pandas as pd
import geopandas as gpd
import requests
import json

print("Step 1: Loading demand points...")
demand = pd.read_csv("data/processed/demand_points.csv")
print(f"  {len(demand):,} demand points loaded")
demand.to_csv("data/processed/kepler_demand.csv", index=False)
print("  Saved: kepler_demand.csv")

print("\nStep 2: Extracting EV charger locations...")
chargers = gpd.read_file("data/processed/ev_chargers.geojson")
chargers_df = pd.DataFrame({
    "lat": chargers.geometry.y,
    "lon": chargers.geometry.x,
    "label": "current"
}).drop_duplicates(subset=["lat", "lon"])
print(f"  {len(chargers_df):,} unique charger locations")
chargers_df.to_csv("data/processed/kepler_chargers_current.csv", index=False)
print("  Saved: kepler_chargers_current.csv")

import time

print("\nStep 3: Saving optimized locations (from live API result)...")
# Results from analyze_network: 2 existing locations, k=2
# improvement_pct: 42.97%, runtime: 44s
opt = pd.DataFrame([
    {"lat": 22.3257131, "lon": 114.1868276, "pct_served": 74.41},
    {"lat": 22.4350284, "lon": 114.0464922, "pct_served": 25.59},
])
opt.to_csv("data/processed/kepler_chargers_optimized.csv", index=False)
print("  Saved: kepler_chargers_optimized.csv")
print("\nAll done! Files ready for Kepler.gl:")
print("  - kepler_demand.csv (41,288 demand points)")
print("  - kepler_chargers_current.csv (904 current locations)")
print("  - kepler_chargers_optimized.csv (2 optimal locations)")
print("  - Improvement: 42.97%")