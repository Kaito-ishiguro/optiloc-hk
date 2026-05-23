"""
notebooks/23_solve_kmedian_road.py

Road-network k-median (k=5, 3 restarts).
Assignment : Dijkstra from each facility node to all demand nodes.
Location   : population-weighted centroid → snap to nearest road node.
Compare per-resident road distance against road-network Weber (file 22).
"""

from pathlib import Path
import time
import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx

ROOT     = Path(__file__).resolve().parent.parent
DATA     = ROOT / "data" / "processed"
GRAPH_ML = DATA / "hk_road_network.graphml"
AGG_CSV  = DATA / "demand_nodes_aggregated.csv"

K          = 5
N_RESTARTS = 3
MAX_ITERS  = 15
RNG_SEED   = 42

# ── load graph + demand nodes ────────────────────────────────────────────────
print("Loading road network...")
G_dir = ox.load_graphml(GRAPH_ML)
G     = G_dir.to_undirected()
print(f"  {len(G.nodes):,} nodes  |  {len(G.edges):,} edges")

print("Loading aggregated demand nodes...")
agg          = pd.read_csv(AGG_CSV)
demand_nodes = agg["road_node"].values.tolist()
demand_lats  = agg["lat"].values
demand_lons  = agg["lon"].values
weights      = agg["weight"].values
N            = len(demand_nodes)
TOTAL_W      = weights.sum()
print(f"  {N:,} demand nodes  |  total weight {TOTAL_W:,.0f}")

# ── one Lloyd restart ─────────────────────────────────────────────────────────
def lloyd_one_restart(seed: int, restart_id: int) -> tuple:
    rng       = np.random.default_rng(seed)
    fac_nodes = list(rng.choice(demand_nodes, size=K, replace=False))
    prev_asgn = None

    for it in range(1, MAX_ITERS + 1):
        # assignment: Dijkstra from each facility
        dist_matrix = np.full((N, K), np.inf)
        for j, fn in enumerate(fac_nodes):
            lengths = nx.single_source_dijkstra_path_length(G, fn, weight="length")
            dist_matrix[:, j] = [lengths.get(dn, np.inf) for dn in demand_nodes]

        asgn = dist_matrix.argmin(axis=1)
        if prev_asgn is not None and np.array_equal(asgn, prev_asgn):
            print(f"  Restart {restart_id}  iter {it:2d}: stable")
            break
        prev_asgn = asgn.copy()

        # location: weighted centroid → snap to nearest road node
        new_fac = []
        for j in range(K):
            mask = asgn == j
            if not mask.any():
                new_fac.append(fac_nodes[j])
                continue
            w_j   = weights[mask]
            tot   = w_j.sum()
            c_lat = (w_j * demand_lats[mask]).sum() / tot
            c_lon = (w_j * demand_lons[mask]).sum() / tot
            new_fac.append(ox.nearest_nodes(G_dir, X=c_lon, Y=c_lat))
        fac_nodes = new_fac

    obj = float((weights * dist_matrix[np.arange(N), asgn]).sum())
    print(f"  Restart {restart_id}  obj={obj:,.1f}  ({obj/TOTAL_W:,.1f} m/resident)")
    return fac_nodes, asgn, obj

# ── multi-start ───────────────────────────────────────────────────────────────
print(f"\nRunning {N_RESTARTS} restarts  (k={K}, max_iters={MAX_ITERS})...")
t0      = time.time()
results = [lloyd_one_restart(RNG_SEED + r * 17, r + 1) for r in range(N_RESTARTS)]
elapsed = time.time() - t0

best_fac, best_asgn, best_obj = min(results, key=lambda x: x[2])

# ── report ────────────────────────────────────────────────────────────────────
WEBER_ROAD_OBJ    = 96_196_423_875.0      # from file 22
reduction_pct     = (WEBER_ROAD_OBJ - best_obj) / WEBER_ROAD_OBJ * 100

print(f"\n{'─'*60}")
print(f"  Road-network k-median  (k={K})")
print(f"  Best objective    : {best_obj:,.1f} m")
print(f"  Per resident      : {best_obj/TOTAL_W:,.1f} m")
print(f"  vs road Weber (1) : {WEBER_ROAD_OBJ/TOTAL_W:,.1f} m/resident")
print(f"  Reduction         : {reduction_pct:.1f}%")
print(f"  Elapsed           : {elapsed:.1f}s")
print()
print("  Facility locations:")
for j, fn in enumerate(best_fac):
    lat = G.nodes[fn]["y"]
    lon = G.nodes[fn]["x"]
    pop = weights[best_asgn == j].sum()
    print(f"    F{j+1}: ({lat:.5f}, {lon:.5f})  serves {pop:,.0f} residents"
          f"  ({pop/TOTAL_W*100:.1f}%)")
print(f"{'─'*60}")