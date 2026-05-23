"""
notebooks/22_solve_weber_road.py

Discrete road-network Weber problem.
Facility must sit on a road node. Local search on the graph:
  - evaluate current node and all neighbours via Dijkstra
  - move to best neighbour if it improves the objective
  - repeat until locally optimal
Multi-start from 3 seeds. Compare result to Euclidean optimum.
"""

from pathlib import Path
import time
import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx

# ── paths ────────────────────────────────────────────────────────────────────
ROOT    = Path(__file__).resolve().parent.parent
DATA    = ROOT / "data" / "processed"
GRAPH_ML = DATA / "hk_road_network.graphml"
AGG_CSV  = DATA / "demand_nodes_aggregated.csv"

# ── euclidean optimum (from notebooks/08) ────────────────────────────────────
EUCLIDEAN_OPT = (22.33729, 114.17071)   # (lat, lon)

# ── load graph (undirected for symmetric road distances) ─────────────────────
print("Loading road network...")
G_dir = ox.load_graphml(GRAPH_ML)
G     = G_dir.to_undirected()
print(f"  {len(G.nodes):,} nodes  |  {len(G.edges):,} edges")

# ── load aggregated demand nodes ─────────────────────────────────────────────
print("Loading aggregated demand nodes...")
agg          = pd.read_csv(AGG_CSV)
demand_nodes = agg["road_node"].tolist()
weights      = agg["weight"].values
print(f"  {len(demand_nodes):,} unique demand nodes  |  total weight {weights.sum():,.0f}")

# ── objective: total weighted road distance from a node to all demand nodes ──
def objective(node: int) -> float:
    lengths = nx.single_source_dijkstra_path_length(G, node, weight="length")
    return float(sum(weights[i] * lengths.get(demand_nodes[i], np.inf)
                     for i in range(len(demand_nodes))))

# ── local search from a single starting node ─────────────────────────────────
def local_search(start: int, label: str = "") -> tuple[int, float, int]:
    current     = start
    current_obj = objective(current)
    iters       = 0

    for iters in range(1, 501):
        neighbours  = list(G.neighbors(current))
        best_node   = current
        best_obj    = current_obj

        for nb in neighbours:
            obj = objective(nb)
            if obj < best_obj:
                best_obj  = obj
                best_node = nb

        if best_node == current:
            break
        current     = best_node
        current_obj = best_obj

    lat = G.nodes[current]["y"]
    lon = G.nodes[current]["x"]
    print(f"  [{label}] converged in {iters} step(s)  →  "
          f"({lat:.5f}, {lon:.5f})  obj={current_obj:,.1f}")
    return current, current_obj, iters

# ── three starting seeds ─────────────────────────────────────────────────────
# seed 1: nearest node to Euclidean Weber optimum
seed1 = ox.nearest_nodes(G_dir,
                         X=EUCLIDEAN_OPT[1],
                         Y=EUCLIDEAN_OPT[0])

# seed 2: highest-weight demand node
seed2 = int(agg.loc[agg["weight"].idxmax(), "road_node"])

# seed 3: 10th-highest weight (diversity)
seed3 = int(agg.nlargest(10, "weight").iloc[9]["road_node"])

print("\nRunning multi-start local search...")
t0      = time.time()
results = []
for seed, label in [(seed1, "near Euclidean opt"),
                    (seed2, "max-weight node"),
                    (seed3, "10th-weight node")]:
    node, obj, iters = local_search(seed, label)
    results.append((node, obj, iters))
elapsed = time.time() - t0

# ── best result ───────────────────────────────────────────────────────────────
best_node, best_obj, _ = min(results, key=lambda r: r[1])
best_lat = G.nodes[best_node]["y"]
best_lon = G.nodes[best_node]["x"]

# ── compare with Euclidean optimum ───────────────────────────────────────────
shift_m = ox.distance.great_circle(
    EUCLIDEAN_OPT[0], EUCLIDEAN_OPT[1], best_lat, best_lon
)

print(f"\n{'─'*55}")
print(f"  Road-network Weber optimum")
print(f"    Node ID  : {best_node}")
print(f"    Location : ({best_lat:.5f}, {best_lon:.5f})")
print(f"    Objective: {best_obj:,.1f} m (total pop-weighted road distance)")
print(f"  Euclidean optimum : {EUCLIDEAN_OPT}")
print(f"  Shift             : {shift_m:.1f} m  ({shift_m/1000:.3f} km)")
print(f"  Elapsed           : {elapsed:.1f}s")
print(f"{'─'*55}")