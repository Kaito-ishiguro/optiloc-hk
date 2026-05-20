"""
notebooks/10_fetch_ozp.py

Fetch all 11,963 Hong Kong Outline Zoning Plan polygons from Esri
China HK's public ArcGIS REST feature service, paginated, and save
as a single GeoJSON file with geometries reprojected to WGS84.

The full unfiltered dataset is cached so downstream filters (commercial,
industrial, mixed-use, etc.) can be re-run without hitting the API again.
This mirrors the GCP "Cloud Function -> GCS bucket -> downstream consumers"
pattern at the local-development scale.
"""

import json
import time
from pathlib import Path

import requests

# ---- Configuration ----
SERVICE_URL = (
    "https://services3.arcgis.com/6j1KwZfY2fZrfNMR"
    "/arcgis/rest/services/ZONE/FeatureServer/0/query"
)
PAGE_SIZE = 2000          # matches the service's maxRecordCount
TOTAL_EXPECTED = 11963    # from earlier returnCountOnly query

OUTPUT_PATH = (
    Path(__file__).parent.parent
    / "data" / "processed" / "ozp_all_zones.geojson"
)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def fetch_page(offset: int) -> dict:
    """Fetch one page of features as a GeoJSON FeatureCollection."""
    params = {
        "where": "1=1",
        "outFields": "OBJECTID,PLAN_NO,ZONE_LABEL,DESC_ENG,SPUSE_ENG",
        "outSR": "4326",                  # WGS84; server reprojects from HK1980 Grid
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": PAGE_SIZE,
        "orderByFields": "OBJECTID",      # stable pagination order
    }
    response = requests.get(SERVICE_URL, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def main():
    all_features = []
    offset = 0
    page_num = 0

    print(f"Fetching {TOTAL_EXPECTED} features in pages of {PAGE_SIZE}...")
    print()

    while True:
        page_num += 1
        print(f"  Page {page_num}: offset={offset:>5} ...", end=" ", flush=True)
        t0 = time.time()
        page = fetch_page(offset)
        features = page.get("features", [])
        elapsed = time.time() - t0
        print(f"got {len(features):>4} features in {elapsed:.2f}s")

        if not features:
            break

        all_features.extend(features)

        if len(features) < PAGE_SIZE:
            break  # last (partial) page

        offset += PAGE_SIZE

    print()
    print(f"Total fetched: {len(all_features)}  (expected {TOTAL_EXPECTED})")
    if len(all_features) != TOTAL_EXPECTED:
        print("WARNING: count mismatch -- something changed upstream")

    output = {
        "type": "FeatureCollection",
        "features": all_features,
        "crs": {
            "type": "name",
            "properties": {"name": "EPSG:4326"},
        },
    }

    print(f"Writing to {OUTPUT_PATH} ...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f)
    size_mb = OUTPUT_PATH.stat().st_size / 1e6
    print(f"Wrote {size_mb:.1f} MB")


if __name__ == "__main__":
    main()