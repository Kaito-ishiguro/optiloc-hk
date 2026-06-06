"""Notebook 25 — Phase 1b: congestion overlay from data.gov.hk.

Joins observed road segment speeds (TD traffic detector feed, processed data)
onto the osmnx graph edges, producing a 'travel_time_peak' edge attribute that
captures real-world conditions (slower than free-flow on arterials).

Data sources:
  - irnAvgSpeed-all.xml        : live speed feed (segment_id → speed_kph, valid)
  - speed_segments_info.csv    : IRN segment info (irn_id → route name)
  - RdNet_IRNP.gdb.zip         : Road Network 2nd Gen (IRN segment geometry)
  - hk_road_network.graphml    : existing osmnx graph (Phase 1a augmented)

Join strategy: geometry proximity
  1. Extract centerline midpoint of each IRN segment from FGDB
  2. Find nearest osmnx edge to each midpoint
  3. For valid segments, assign observed_speed to that osmnx edge
  4. Recompute travel_time_peak = length / (observed_speed / 3.6)
  5. Edges with no IRN coverage keep free-flow travel_time (Phase 1a)

NOTE on timing: the XML feed is captured at whatever time the script is run.
For true AM peak, capture data between 07:30–09:30 HK time on a weekday.
The collection script (at end of this file) can be run via Task Scheduler or
manually at 8am. The historical archive (data.gov.hk) only archives midnight
snapshots, not hourly ones.

Run from optiloc-hk:
    & "C:\\...\\python.exe" notebooks/25_travel_time_phase1b_congestion.py
    # --xml path can override the default captured file
"""

import sys
import zipfile
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
import osmnx as ox
import pandas as pd
import geopandas as gpd
import pyogrio
import networkx as nx
from shapely.geometry import Point, LineString

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from api.travel_time import augment_graph_with_travel_times

# ── paths ──────────────────────────────────────────────────────────────────────
DATA_DIR      = REPO_ROOT / "data" / "processed"
RAW_DIR       = REPO_ROOT / "data" / "raw"
ROAD_GRAPH_ML = DATA_DIR / "hk_road_network.graphml"
AGG_CSV       = DATA_DIR / "demand_nodes_aggregated.csv"

SPEED_XML     = RAW_DIR / "traffic_speed_current.xml"   # override with --xml
SEG_INFO_CSV  = RAW_DIR / "speed_segments_info.csv"
FGDB_ZIP      = RAW_DIR / "RdNet_IRNP.gdb.zip"
FGDB_DIR      = RAW_DIR / "RdNet_IRNP.gdb"

# Output: enriched graph (not committed; used by downstream scripts)
OUT_AUGMENTED_GRAPHML = DATA_DIR / "hk_road_network_peak.graphml"


def sep(title: str = "", width: int = 65) -> None:
    if title:
        print(f"\n{'─' * 5}  {title}  {'─' * max(0, width - len(title) - 9)}")
    else:
        print("─" * width)


# ── 1. Parse the speed XML ─────────────────────────────────────────────────────

def parse_speed_xml(xml_path: Path) -> tuple[dict[int, float], str]:
    """Returns ({segment_id: speed_kph} for valid segments, capture_timestamp)."""
    import xml.etree.ElementTree as ET
    root = ET.parse(xml_path).getroot()
    date = root.findtext("date") or "unknown"
    time = root.findtext("time") or "unknown"
    timestamp = f"{date} {time}"
    speeds = {}
    for seg in root.findall(".//segment"):
        if seg.findtext("valid") == "Y":
            sid = int(seg.findtext("segment_id"))
            spd = float(seg.findtext("speed"))
            speeds[sid] = spd
    return speeds, timestamp


# ── 2. Load FGDB geometry ──────────────────────────────────────────────────────

def extract_fgdb_if_needed(zip_path: Path, out_dir: Path) -> None:
    """Unzip the FGDB if not already extracted."""
    if out_dir.exists():
        return
    print(f"  Extracting {zip_path.name} → {out_dir.name}/")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir.parent)


def load_irn_centerlines(fgdb_dir: Path) -> gpd.GeoDataFrame:
    """Load the road centerline layer from the FGDB and return with irn_id."""
    layers = pyogrio.list_layers(str(fgdb_dir))
    print(f"  FGDB layers: {[l[0] for l in layers]}")

    # Try common layer names for the centerline with IRN IDs.
    preferred = ["LINK", "CENTERLINE", "RoadLink", "road_link", "irn_link"]
    target_layer = None
    for lname in preferred:
        if any(lname.upper() == str(l[0]).upper() for l in layers):
            target_layer = lname
            break
    if target_layer is None:
        target_layer = layers[0][0]
        print(f"  Using first layer: {target_layer}")
    else:
        print(f"  Using layer: {target_layer}")

    gdf = gpd.read_file(str(fgdb_dir), layer=target_layer)
    gdf = gdf.to_crs(epsg=4326)   # WGS84 for lat/lon arithmetic
    print(f"  Loaded {len(gdf):,} features, columns: {list(gdf.columns)[:10]}")
    return gdf


def find_irn_id_column(gdf: gpd.GeoDataFrame) -> str | None:
    """Guess which column holds the IRN segment ID.

    In the TD Road Network 2nd Gen FGDB (RdNet_IRNP.gdb), the CENTERLINE layer
    uses ROUTE_ID as its primary key, which matches the segment_id values in the
    irnAvgSpeed XML feed (verified: 99.6% overlap).
    """
    candidates = ["ROUTE_ID", "IRN_ID", "irn_id", "LINK_ID", "OBJECTID", "FID", "ID", "SEG_ID"]
    cols_upper = {c.upper(): c for c in gdf.columns}
    for cand in candidates:
        if cand.upper() in cols_upper:
            return cols_upper[cand.upper()]
    return None


# ── 3. Geometric join: IRN segments → osmnx edges ─────────────────────────────

def build_edge_speed_map(
    gdf: gpd.GeoDataFrame,
    irn_id_col: str,
    speeds: dict[int, float],
    G_dir,
) -> dict[tuple, float]:
    """Map each osmnx undirected edge (u, v) to an observed speed (km/h).

    Strategy:
      1. Filter GDF to segments that have valid observed speed.
      2. For each segment, compute centroid in WGS84.
      3. Find nearest osmnx edge to that centroid.
      4. If multiple IRN segments map to the same edge, take the mean speed.
    """
    # Build a lookup: osmnx node positions for snapping
    edges = list(G_dir.edges(data=True))
    # Build a simple point-in-edge lookup using edge midpoints
    edge_midpoints = []
    edge_keys = []
    for u, v, data in edges:
        x_u, y_u = G_dir.nodes[u]["x"], G_dir.nodes[u]["y"]
        x_v, y_v = G_dir.nodes[v]["x"], G_dir.nodes[v]["y"]
        mid_x = (x_u + x_v) / 2
        mid_y = (y_u + y_v) / 2
        edge_midpoints.append(Point(mid_x, mid_y))
        edge_keys.append((u, v))

    edge_mid_gdf = gpd.GeoDataFrame(
        {"u": [k[0] for k in edge_keys], "v": [k[1] for k in edge_keys]},
        geometry=edge_midpoints,
        crs="EPSG:4326",
    )
    # Project to HK local CRS for accurate distance computation
    edge_mid_proj = edge_mid_gdf.to_crs("EPSG:2326")

    # Filter IRN segments to those with observed speed
    gdf_with_speed = gdf[gdf[irn_id_col].isin(speeds)].copy()
    print(f"  IRN segments with observed speed: {len(gdf_with_speed):,}")

    # Compute centroids (projected for accuracy)
    gdf_proj = gdf_with_speed.to_crs("EPSG:2326")
    gdf_proj["centroid"] = gdf_proj.geometry.centroid

    # For each IRN segment, find nearest edge midpoint
    edge_speed_acc: dict[tuple, list[float]] = {}
    centroids_gdf = gpd.GeoDataFrame(
        {"irn_id": gdf_with_speed[irn_id_col].values},
        geometry=gdf_proj["centroid"].values,
        crs="EPSG:2326",
    )
    joined = gpd.sjoin_nearest(centroids_gdf, edge_mid_proj, how="left")
    joined["speed"] = joined["irn_id"].map(speeds)

    for _, row in joined.iterrows():
        key = (int(row["u"]), int(row["v"]))
        if key not in edge_speed_acc:
            edge_speed_acc[key] = []
        edge_speed_acc[key].append(float(row["speed"]))

    # Average where multiple IRN segments → same edge
    edge_speed_map = {k: float(np.mean(v)) for k, v in edge_speed_acc.items()}
    return edge_speed_map


# ── 4. Augment osmnx graph with peak travel times ─────────────────────────────

def apply_peak_travel_times(
    G_dir,
    edge_speed_map: dict[tuple, float],
) -> tuple[int, int]:
    """Add 'travel_time_peak' to every directed edge.

    For edges with an observed speed: travel_time_peak = length / (speed / 3.6)
    For edges without observed speed: keep travel_time from Phase 1a free-flow.

    Returns (n_observed, n_free_flow) edge counts.
    """
    n_observed = 0
    n_free_flow = 0
    for u, v, k, data in G_dir.edges(keys=True, data=True):
        key_fwd = (u, v)
        key_rev = (v, u)
        obs_speed = edge_speed_map.get(key_fwd) or edge_speed_map.get(key_rev)
        if obs_speed is not None:
            length = data.get("length", 0.0)
            ff_time = data.get("travel_time", length)  # free-flow (Phase 1a)
            obs_time = length / (obs_speed / 3.6)
            # Cap: peak cannot be faster than free-flow. If observed speed
            # exceeds imputed free-flow (geometry mismatch or conservative
            # OSM imputation), keep free-flow rather than a spuriously fast peak.
            data["travel_time_peak"] = max(obs_time, ff_time)
            n_observed += 1
        else:
            data["travel_time_peak"] = data.get("travel_time", data.get("length", 0.0))
            n_free_flow += 1
    return n_observed, n_free_flow


# ── 5. Validation: peak vs free-flow on arterials ─────────────────────────────

def validate_peak_vs_freeflow(G_dir, edge_speed_map: dict[tuple, float]) -> None:
    """Confirm peak travel times are >= free-flow on observed edges."""
    violations = 0
    comparisons = 0
    speedups = []
    slowdowns = []
    for u, v, k, data in G_dir.edges(keys=True, data=True):
        tt_free = data.get("travel_time")
        tt_peak = data.get("travel_time_peak")
        if tt_free is None or tt_peak is None:
            continue
        comparisons += 1
        ratio = tt_peak / tt_free if tt_free > 0 else 1.0
        if ratio < 0.999:  # allow floating point tolerance
            violations += 1
        if (u, v) in edge_speed_map or (v, u) in edge_speed_map:
            slowdowns.append(ratio)

    print(f"  Edges compared      : {comparisons:,}")
    print(f"  Violations (peak<ff): {violations} (expect 0)")
    if slowdowns:
        print(f"  Observed edges congestion ratio (peak/free-flow):")
        print(f"    min: {min(slowdowns):.2f}  mean: {np.mean(slowdowns):.2f}  "
              f"max: {max(slowdowns):.2f}")
        print(f"    (>1 = slower than free-flow; 1.0 = same speed)")


def sample_1median_comparison(
    G, G_dir,
    demand_nodes: list[int],
    demand_weights: np.ndarray,
    demand_lats: np.ndarray,
    demand_lons: np.ndarray,
    n_sample: int = 500,
) -> None:
    """Quick 1-median spot-check on a random subsample to show time_peak shift.

    Uses a 1-step local search from the centroid seed only — not a full
    Maranzana search — because this is a validation sample, not a production run.
    """
    rng = np.random.default_rng(42)
    idx = rng.choice(len(demand_nodes), size=min(n_sample, len(demand_nodes)), replace=False)
    s_nodes = [demand_nodes[i] for i in idx]
    s_weights = demand_weights[idx]
    s_lats = demand_lats[idx]
    s_lons = demand_lons[idx]

    c_lat = float(np.average(s_lats, weights=s_weights))
    c_lon = float(np.average(s_lons, weights=s_weights))
    seed = int(ox.nearest_nodes(G_dir, X=c_lon, Y=c_lat))
    total_w = s_weights.sum()

    def obj(node, weight_key):
        lengths = nx.single_source_dijkstra_path_length(G, node, weight=weight_key)
        return sum(s_weights[i] * lengths.get(s_nodes[i], 1e9) for i in range(len(s_nodes)))

    obj_dist = obj(seed, "length")
    obj_ff   = obj(seed, "travel_time")
    obj_peak = obj(seed, "travel_time_peak")

    print(f"\n  Centroid-seed objective on {n_sample}-node subsample:")
    print(f"    Distance    : {obj_dist/total_w:,.1f} m/resident")
    print(f"    Free-flow   : {obj_ff/total_w:,.1f} s/resident  "
          f"({obj_ff/total_w/60:.2f} min/resident)")
    print(f"    Peak        : {obj_peak/total_w:,.1f} s/resident  "
          f"({obj_peak/total_w/60:.2f} min/resident)")
    print(f"    Peak/FF ratio: {obj_peak/obj_ff:.3f}  "
          f"({'SLOWER as expected' if obj_peak >= obj_ff else 'FASTER — check data'})")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", default=str(SPEED_XML),
                        help="Path to speed XML snapshot (default: data/raw/traffic_speed_current.xml)")
    args = parser.parse_args()
    xml_path = Path(args.xml)

    sep("1. Parse speed XML")
    if not xml_path.exists():
        print(f"  ERROR: {xml_path} not found. Download it first:")
        print(f"  Invoke-WebRequest 'https://resource.data.one.gov.hk/td/traffic-detectors/irnAvgSpeed-all.xml' -OutFile '{xml_path}'")
        sys.exit(1)
    speeds, timestamp = parse_speed_xml(xml_path)
    print(f"  Snapshot time       : {timestamp}")
    print(f"  Valid segments      : {len(speeds):,}")
    speed_vals = list(speeds.values())
    print(f"  Speed range         : {min(speed_vals):.1f} – {max(speed_vals):.1f} km/h  "
          f"(mean {np.mean(speed_vals):.1f} km/h)")
    print()
    is_am_peak = False
    if timestamp != "unknown":
        try:
            h = int(timestamp.split()[1].split(":")[0])
            is_am_peak = 7 <= h <= 10
        except Exception:
            pass
    if not is_am_peak:
        print("  NOTE: snapshot is NOT AM peak (7:30–9:30 HK). The pipeline is")
        print("  correct; run again at AM peak for congestion-accurate results.")
        print("  (Historical archive only stores midnight snapshots.)")

    sep("2. Load FGDB segment geometry")
    if not FGDB_ZIP.exists():
        print(f"  ERROR: {FGDB_ZIP} not found. Download it first:")
        print(f"  Invoke-WebRequest 'https://static.data.gov.hk/td/road-network-v2/RdNet_IRNP.gdb.zip' -OutFile '{FGDB_ZIP}'")
        sys.exit(1)
    extract_fgdb_if_needed(FGDB_ZIP, FGDB_DIR)
    gdf = load_irn_centerlines(FGDB_DIR)
    irn_col = find_irn_id_column(gdf)
    if irn_col is None:
        print(f"  Could not identify IRN ID column. Available columns: {list(gdf.columns)}")
        print("  Update find_irn_id_column() with the correct column name.")
        sys.exit(1)
    print(f"  IRN ID column       : {irn_col}")
    gdf_ids = set(gdf[irn_col].dropna().astype(int))
    speed_ids = set(speeds.keys())
    overlap = gdf_ids & speed_ids
    print(f"  FGDB IRN IDs        : {len(gdf_ids):,}  range {min(gdf_ids)}–{max(gdf_ids)}")
    print(f"  Speed XML IDs       : {len(speed_ids):,}  range {min(speed_ids)}–{max(speed_ids)}")
    print(f"  Overlapping IDs     : {len(overlap):,}  ({100*len(overlap)/len(speed_ids):.1f}% of speed segments matched)")

    sep("3. Load road graph + augment with free-flow speeds")
    print("  Loading graphml (may take ~20s)...")
    G_dir = ox.load_graphml(ROAD_GRAPH_ML)
    print(f"  Graph: {G_dir.number_of_nodes():,} nodes, {G_dir.number_of_edges():,} directed edges")
    augment_graph_with_travel_times(G_dir)
    G = G_dir.to_undirected()

    sep("4. Geometric join: IRN segments → osmnx edges")
    print("  Computing nearest-edge for each IRN segment centroid...")
    edge_speed_map = build_edge_speed_map(gdf, irn_col, speeds, G_dir)
    n_edges_total = G_dir.number_of_edges()
    print(f"  Osmnx edges with observed speed: {len(edge_speed_map):,} / {n_edges_total:,}  "
          f"({100*len(edge_speed_map)/n_edges_total:.1f}%)")

    sep("5. Apply peak travel times to graph")
    n_obs, n_ff = apply_peak_travel_times(G_dir, edge_speed_map)
    G_peak = G_dir.to_undirected()
    print(f"  Edges with observed speed   : {n_obs:,}  ({100*n_obs/n_edges_total:.1f}%)")
    print(f"  Edges using free-flow speed : {n_ff:,}  ({100*n_ff/n_edges_total:.1f}%)")

    sep("6. Validate: peak >= free-flow on observed edges")
    validate_peak_vs_freeflow(G_dir, edge_speed_map)

    sep("7. Demand nodes + 1-median spot-check")
    agg = pd.read_csv(AGG_CSV)
    demand_nodes   = [int(n) for n in agg["road_node"]]
    demand_weights = agg["weight"].values.astype(float)
    demand_lats    = agg["lat"].values.astype(float)
    demand_lons    = agg["lon"].values.astype(float)
    print(f"  Demand: {len(demand_nodes):,} nodes, total pop {demand_weights.sum():,.0f}")
    sample_1median_comparison(
        G_peak, G_dir,
        demand_nodes, demand_weights, demand_lats, demand_lons,
        n_sample=500,
    )

    sep("8. Coverage summary (current snapshot)")
    # Quick coverage check: same RedBox branches as Phase 1a
    REDBOX = [
        (22.266475, 114.236692),  # Chai Wan
        (22.287212, 114.133271),  # Sai Wan
        (22.384570, 114.206244),  # Sha Tin
        (22.364570, 114.116238),  # Tsuen Wan
        (22.394972, 113.969905),  # Tuen Mun
        (22.295875, 114.236021),  # Yau Tong
    ]
    branch_nodes = [int(ox.nearest_nodes(G_dir, X=lon, Y=lat)) for lat, lon in REDBOX]

    for metric, weight, lbl in [
        ("distance",  "length",            "Distance (m)"),
        ("free-flow", "travel_time",       "Free-flow time (s)"),
        ("peak",      "travel_time_peak",  "Peak time (s)"),
    ]:
        dist_mat = np.full((len(branch_nodes), len(demand_nodes)), np.inf)
        for i, bn in enumerate(branch_nodes):
            ls = nx.single_source_dijkstra_path_length(G_peak, bn, weight=weight)
            dist_mat[i] = [ls.get(dn, np.inf) for dn in demand_nodes]
        nearest = dist_mat.min(axis=0)
        reachable = np.isfinite(nearest)
        wtd_mean = np.average(nearest[reachable], weights=demand_weights[reachable])
        print(f"  {lbl:<22}: mean {wtd_mean:>9.1f}")

    sep()
    print("\n  Phase 1b complete.")
    print(f"  Snapshot used: {timestamp}  ({xml_path.name})")
    print("  To collect proper AM peak data (7:30–9:30 HK), run at that time:")
    print("    Invoke-WebRequest 'https://resource.data.one.gov.hk/td/traffic-detectors/irnAvgSpeed-all.xml'")
    print("    -OutFile data\\raw\\traffic_speed_ampeak.xml")
    print("  Then re-run with: --xml data\\raw\\traffic_speed_ampeak.xml")


if __name__ == "__main__":
    main()
