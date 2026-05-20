"""
notebooks/11_filter_and_union_ozp.py

Load the cached OZP zones, filter to Commercial (C) and Comprehensive
Development Area (CDA) categories per the email to Prof. Kuo, and
union them into a single (Multi)Polygon that becomes the feasibility
region for the next iteration of the constrained Weber solver.

Output is intentionally tiny (one feature, the union geometry) so it
loads instantly downstream — the heavy 120 MB cache stays untouched.
"""

import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import mapping
from shapely.ops import unary_union

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
INPUT_PATH = DATA_DIR / "ozp_all_zones.geojson"
OUTPUT_PATH = DATA_DIR / "ozp_commercial_union.geojson"


def is_commercial_or_cda(label: str) -> bool:
    """
    True for exactly: C, C(1..N), CDA, CDA(1..N).

    Explicitly NOT true for C/R (mixed-use), CA (Conservation Area),
    CP (Country Park), CPA (Coastal Protection Area). These all share
    a 'C' prefix but are not commercial-eligible per our filter.
    """
    if label in ("C", "CDA"):
        return True
    if label.startswith("C(") and label.endswith(")"):
        return True
    if label.startswith("CDA(") and label.endswith(")"):
        return True
    return False


def main():
    print(f"Loading {INPUT_PATH.name} (may take 10-30s for 120 MB) ...")
    gdf = gpd.read_file(INPUT_PATH)
    print(f"  Loaded {len(gdf):,} features")
    print(f"  Geometry types: {gdf.geom_type.value_counts().to_dict()}")
    print(f"  CRS: {gdf.crs}")
    print()

    mask = gdf["ZONE_LABEL"].apply(is_commercial_or_cda)
    commercial = gdf[mask].copy()

    print(f"After C + CDA filter: {len(commercial):,} features")
    print()
    print("Filter breakdown (feature count by ZONE_LABEL):")
    print(commercial["ZONE_LABEL"].value_counts().to_string())
    print()

    # Reproject to HK1980 Grid (meters) just to compute accurate area.
    commercial_m = commercial.to_crs("EPSG:2326")
    total_area_km2 = commercial_m.area.sum() / 1e6
    print(f"Total area of C + CDA zones: {total_area_km2:.2f} km^2")
    print(f"  (HK total land area ~1,106 km^2, so {total_area_km2/1106:.1%})")
    print()

    print("Computing geometric union ...")
    union_geom = unary_union(commercial.geometry.values)
    print(f"  Union geometry type: {union_geom.geom_type}")
    if union_geom.geom_type == "MultiPolygon":
        print(f"  Disjoint polygons in union: {len(union_geom.geoms)}")
    print()

    output = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "description": "Union of all C and CDA OZP zones in HK",
                    "source": "Esri China HK service /ZONE/FeatureServer/0",
                    "filter_rule": (
                        "ZONE_LABEL == 'C' or startswith 'C(' "
                        "or == 'CDA' or startswith 'CDA('"
                    ),
                    "n_input_polygons": int(len(commercial)),
                    "n_output_polygons": (
                        len(union_geom.geoms)
                        if union_geom.geom_type == "MultiPolygon"
                        else 1
                    ),
                    "total_area_km2": round(total_area_km2, 3),
                },
                "geometry": mapping(union_geom),
            }
        ],
    }

    print(f"Writing union to {OUTPUT_PATH.name} ...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f)
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Wrote {size_kb:.1f} KB")


if __name__ == "__main__":
    main()