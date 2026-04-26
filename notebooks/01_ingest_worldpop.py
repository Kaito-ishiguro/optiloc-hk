"""
OptiLoc HK — Session 002a: WorldPop raster -> demand_points.csv

Reads the WorldPop 100m gridded population GeoTIFF for Hong Kong,
extracts every populated pixel, computes its centroid in lat/lon,
and saves a flat CSV with (lat, lon, weight) ready for the Weber
optimization solver.

Why this dataset (vs. census TPU centroids):
We avoid the "centroid trap" — TPU centroids force ~50,000 people
into one coordinate that often falls on a hilltop or in water.
WorldPop gives a 100m grid where each cell directly estimates how
many people live in that 100m x 100m square, so weight distribution
is faithful to where people actually are.

Run from repo root:
    python notebooks/01_ingest_worldpop.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import xy

# ---------- Paths ----------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_RAW / "hkg_ppp_2020_UNadj_constrained.tif"
OUTPUT_FILE = DATA_PROCESSED / "demand_points.csv"

# ---------- Sanity check ----------
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT_FILE}.\n"
        "Download hkg_ppp_2020_UNadj_constrained.tif from HDX and place it in data/raw/."
    )

# ---------- Load and inspect ----------
with rasterio.open(INPUT_FILE) as src:
    print(f"Loaded {INPUT_FILE.name}")
    print(f"  CRS:       {src.crs}")
    print(f"  Shape:     {src.shape}    (rows x cols)")
    print(f"  Bounds:    {src.bounds}")
    print(f"  NoData:    {src.nodata}")
    print(f"  Resolution: {src.res}    (degrees, since EPSG:4326)")

    population = src.read(1)          # band 1 = population count per cell
    transform = src.transform          # maps (row, col) -> (x, y)
    nodata = src.nodata
    crs = src.crs

# ---------- Build mask of valid populated cells ----------
# Drop NoData (unsettled / ocean / parkland)
# Drop zero-weight cells (don't waste solver time on them)
if nodata is not None:
    valid_mask = (population != nodata) & (population > 0)
else:
    valid_mask = population > 0

# Also drop NaN values to be safe (rasterio sometimes returns these)
valid_mask &= ~np.isnan(population)

n_total = population.size
n_valid = valid_mask.sum()
print(f"\n  Total cells:     {n_total:,}")
print(f"  Populated cells: {n_valid:,}    ({100 * n_valid / n_total:.1f}%)")

# ---------- Extract row/col indices and weights ----------
rows, cols = np.where(valid_mask)
weights = population[rows, cols].astype(float)

# ---------- Convert pixel indices to lon/lat coordinates ----------
# rasterio.transform.xy returns the CENTER of each pixel by default,
# which is exactly what we want as the demand-point coordinate.
xs, ys = xy(transform, rows.tolist(), cols.tolist())
xs = np.asarray(xs)
ys = np.asarray(ys)

# WorldPop is published in EPSG:4326 (WGS84). Sanity-confirm.
if crs.to_epsg() != 4326:
    raise RuntimeError(
        f"Expected EPSG:4326 for WorldPop, got {crs}. Reproject before continuing."
    )

# In EPSG:4326: x = longitude, y = latitude
df = pd.DataFrame({
    "lat": ys,
    "lon": xs,
    "weight": weights,
})

# ---------- Defensive bounds clip (HK only) ----------
# Catches any pixels accidentally outside HK due to NoData mis-encoding.
HK_LAT_MIN, HK_LAT_MAX = 22.10, 22.60
HK_LON_MIN, HK_LON_MAX = 113.80, 114.50
before = len(df)
df = df[
    df["lat"].between(HK_LAT_MIN, HK_LAT_MAX)
    & df["lon"].between(HK_LON_MIN, HK_LON_MAX)
].reset_index(drop=True)
if len(df) < before:
    print(f"  Clipped {before - len(df)} cells outside HK bounding box")

# ---------- Summary stats ----------
total_pop = df["weight"].sum()
print(f"\n  Final demand points:    {len(df):,}")
print(f"  Total population:       {total_pop:,.0f}")
print(f"  Min / max / mean weight: {df['weight'].min():.2f} / "
      f"{df['weight'].max():.2f} / {df['weight'].mean():.2f}")
# HK's 2020 population was ~7.5M. If your number is in that ballpark, you're good.

# ---------- Save ----------
df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved -> {OUTPUT_FILE}")
print("This CSV is the input to the Weber gradient-descent solver in Session 003.")
