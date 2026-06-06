"""Assign each road-graph node to one of the 18 HK administrative districts.

Outputs: data/rent/node_to_district.json  — {str(node_id): district_name}

District names match the English name field in the HAD GeoJSON exactly.
Run once locally before deploying; commit the JSON to the public repo so
it is baked into the container.

Usage (from repo root):
    & "...optiloc-hk/.venv/Scripts/python.exe" scripts/precompute_districts.py
"""

import json
import sys
import urllib.request
from pathlib import Path

import osmnx as ox
from shapely.geometry import Point, shape

# ── paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT     = Path(__file__).resolve().parent.parent
ROAD_GRAPH_ML = REPO_ROOT / "data" / "processed" / "hk_road_network.graphml"
OUT_DIR       = REPO_ROOT / "data" / "rent"
OUT_JSON      = OUT_DIR / "node_to_district.json"

BOUNDARY_URL  = (
    "https://www.had.gov.hk/psi/"
    "hong-kong-administrative-boundaries/"
    "hksar_18_district_boundary.json"
)

# ── helpers ───────────────────────────────────────────────────────────────────

def _find_name_field(properties: dict) -> str:
    """Return the property key that holds the English district name.

    Tries common HAD field names in order; raises if none match.
    """
    candidates = ["District", "ENAME", "ENG_NAME", "District_E", "DNAME_E", "NAME_E", "ename"]
    for key in candidates:
        if key in properties:
            return key
    # Last resort: any key whose value looks like an English district name.
    # Print all keys so the user can inspect.
    print("  Available property keys:", list(properties.keys()))
    raise KeyError(
        "Could not detect English-name field in GeoJSON properties. "
        f"Keys seen: {list(properties.keys())}"
    )


def _centroid(geom) -> tuple[float, float]:
    """Return (lon, lat) centroid of a Shapely geometry."""
    c = geom.centroid
    return c.x, c.y


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # 1. Load graph ─────────────────────────────────────────────────────────
    print(f"Loading road graph: {ROAD_GRAPH_ML}")
    if not ROAD_GRAPH_ML.exists():
        sys.exit(f"ERROR: graph file not found at {ROAD_GRAPH_ML}")
    G_dir = ox.load_graphml(ROAD_GRAPH_ML)
    G = G_dir.to_undirected()
    nodes = G.nodes(data=True)
    n_total = G.number_of_nodes()
    print(f"  {n_total:,} nodes, {G.number_of_edges():,} edges")

    # 2. Download district boundaries ───────────────────────────────────────
    print(f"Downloading district boundaries: {BOUNDARY_URL}")
    with urllib.request.urlopen(BOUNDARY_URL, timeout=30) as resp:
        geojson = json.loads(resp.read())
    features = geojson["features"]
    print(f"  {len(features)} district features")

    # Detect the English name field from the first feature.
    name_field = _find_name_field(features[0]["properties"])
    print(f"  Using property field '{name_field}' for district name")

    # Build list of (district_name, shapely_polygon).
    districts: list[tuple[str, object]] = []
    district_centroids: list[tuple[str, float, float]] = []  # (name, lon, lat)
    for feat in features:
        name = feat["properties"][name_field]
        geom = shape(feat["geometry"])
        districts.append((name, geom))
        clon, clat = _centroid(geom)
        district_centroids.append((name, clon, clat))

    # 3. Point-in-polygon assignment ────────────────────────────────────────
    print("Assigning nodes to districts via point-in-polygon …")
    node_to_district: dict[str, str] = {}
    unmatched: list[tuple[int, float, float]] = []

    for node_id, data in nodes:
        lon = float(data["x"])
        lat = float(data["y"])
        pt = Point(lon, lat)
        assigned = None
        for dname, dpoly in districts:
            if dpoly.contains(pt):
                assigned = dname
                break
        if assigned is not None:
            node_to_district[str(node_id)] = assigned
        else:
            unmatched.append((node_id, lon, lat))

    # 4. Nearest-centroid fallback for coastal / boundary nodes ─────────────
    if unmatched:
        print(f"  {len(unmatched):,} nodes outside all polygons — snapping to nearest centroid")
        for node_id, lon, lat in unmatched:
            best_name = min(
                district_centroids,
                key=lambda t: (t[1] - lon) ** 2 + (t[2] - lat) ** 2,
            )[0]
            node_to_district[str(node_id)] = best_name

    # 5. Write output ───────────────────────────────────────────────────────
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(node_to_district, fh, ensure_ascii=False)
    print(f"\nWrote {len(node_to_district):,} node→district mappings to:\n  {OUT_JSON}")

    # 6. Summary ────────────────────────────────────────────────────────────
    from collections import Counter
    counts = Counter(node_to_district.values())
    print(f"\nNodes per district ({len(counts)} districts found):")
    for dname, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {dname:<28} {cnt:>6,}")
    print(f"\nUnmatched (coastal, snapped): {len(unmatched):,} / {n_total:,}")
    if len(counts) < 18:
        missing = {d for f in features for d in [f["properties"][name_field]]} - set(counts)
        print(f"WARNING: {len(missing)} districts have zero nodes: {missing}")


if __name__ == "__main__":
    main()
