"""
notebooks/21_road_network_prep.py

Download HK driving road network via osmnx, snap 41k demand points to
nearest road nodes, aggregate to unique nodes, save augmented CSVs.
"""

from pathlib import Path
import pandas as pd
import osmnx as ox

# ── paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
DATA_DIR   = ROOT / "data" / "processed"
DEMAND_CSV = DATA_DIR / "demand_points.csv"
GRAPH_ML   = DATA_DIR / "hk_road_network.graphml"
ROAD_CSV   = DATA_DIR / "demand_points_road.csv"
AGG_CSV    = DATA_DIR / "demand_nodes_aggregated.csv"

# ── load demand points ───────────────────────────────────────────────────────
print("Loading demand points...")
df = pd.read_csv(DEMAND_CSV)
print(f"  {len(df):,} points  |  total weight {df['weight'].sum():,.0f}")

# ── download or load road network ────────────────────────────────────────────
if GRAPH_ML.exists():
    print("Loading cached road network...")
    G = ox.load_graphml(GRAPH_ML)
else:
    print("Downloading HK driving network from OSM (1-3 min)...")
    G = ox.graph_from_place("Hong Kong", network_type="drive")
    ox.save_graphml(G, filepath=GRAPH_ML)
    print(f"  Saved to {GRAPH_ML}")

print(f"  Network: {len(G.nodes):,} nodes  |  {len(G.edges):,} edges")

# ── snap demand points to nearest road nodes ─────────────────────────────────
print("Snapping demand points to nearest road nodes...")
df["road_node"] = ox.nearest_nodes(G, X=df["lon"].values, Y=df["lat"].values)
unique_nodes    = df["road_node"].nunique()
print(f"  {unique_nodes:,} unique road nodes  (from {len(df):,} demand points)")
df.to_csv(ROAD_CSV, index=False)
print(f"  Saved augmented demand points → {ROAD_CSV.name}")

# ── aggregate to unique nodes (demand weight pooled per node) ────────────────
print("Aggregating to unique road nodes...")
agg = df.groupby("road_node")["weight"].sum().reset_index()
agg.columns = ["road_node", "weight"]
agg["lat"] = agg["road_node"].map(lambda n: G.nodes[n]["y"])
agg["lon"] = agg["road_node"].map(lambda n: G.nodes[n]["x"])
agg = agg[["road_node", "lat", "lon", "weight"]].reset_index(drop=True)

print(f"  Aggregated nodes : {len(agg):,}")
print(f"  Weight check     : {agg['weight'].sum():,.0f}")
agg.to_csv(AGG_CSV, index=False)
print(f"  Saved aggregated demand nodes → {AGG_CSV.name}")
print("Done.")