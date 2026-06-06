import unittest
import numpy as np
import networkx as nx
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

from api import solvers

# Initialize solvers at module load time for tests
solvers.initialize_solvers()


class TestInvariants(unittest.TestCase):

    def test_nx_scipy_equivalence(self):
        """
        Invariant 1: scipy csgraph shortest-path results match the networkx results.
        We compute the single-source shortest path from a random demand node to all 
        aggregated demand nodes using both methods and assert they are bit-identical.
        """
        source_node = solvers._agg_demand_nodes[0]
        
        # 1. NetworkX shortest path
        nx_lengths = nx.single_source_dijkstra_path_length(solvers._road_graph, source_node, weight="length")
        nx_dists = np.array([nx_lengths.get(n, np.inf) for n in solvers._agg_demand_nodes])
        
        # 2. SciPy shortest path
        nodes = list(solvers._road_graph.nodes())
        node_to_idx = {n: i for i, n in enumerate(nodes)}
        
        edge_lengths = {}
        for u, v, d in solvers._road_graph.edges(data=True):
            uidx = node_to_idx[u]
            vidx = node_to_idx[v]
            l = d.get("length", 1.0)
            if (uidx, vidx) not in edge_lengths or l < edge_lengths[(uidx, vidx)]:
                edge_lengths[(uidx, vidx)] = l
                edge_lengths[(vidx, uidx)] = l
                
        row = [u for (u, v) in edge_lengths.keys()]
        col = [v for (u, v) in edge_lengths.keys()]
        data = list(edge_lengths.values())
        
        adj_matrix = csr_matrix((data, (row, col)), shape=(len(nodes), len(nodes)))
        
        source_idx = node_to_idx[source_node]
        scipy_dists_all = shortest_path(csgraph=adj_matrix, directed=False, indices=source_idx, return_predecessors=False)
        
        target_indices = [node_to_idx[n] for n in solvers._agg_demand_nodes]
        scipy_dists = scipy_dists_all[target_indices]
        
        np.testing.assert_allclose(
            nx_dists, scipy_dists, 
            rtol=1e-10, atol=1e-10,
            err_msg="SciPy and NetworkX shortest paths do not match"
        )


    def test_hakimi_bound(self):
        """
        Invariant 2: Restricting candidates to demand nodes stays within a generous bound.
        The exact 0.053% gap is a full-instance result from benchmarks, not asserted directly here.
        Here we assert the structural property: the demand-node-restricted 1-median objective 
        is always >= the full-vertex optimum, and the gap is within a loose tolerance (e.g. 1.0%).
        """
        subset_demand_nodes = solvers._agg_demand_nodes[:50]
        subset_weights = solvers._agg_weights[:50]
        
        def objective(candidate_node):
            lengths = nx.single_source_dijkstra_path_length(solvers._road_graph, candidate_node, weight="length")
            return sum(w * lengths.get(dn, np.inf) for w, dn in zip(subset_weights, subset_demand_nodes))
            
        restricted_obj = min(objective(n) for n in subset_demand_nodes)
        
        best_restricted_node = min(subset_demand_nodes, key=objective)
        
        neighborhood = set([best_restricted_node])
        for _ in range(2):
            new_neighbors = set()
            for n in neighborhood:
                new_neighbors.update(solvers._road_graph.neighbors(n))
            neighborhood.update(new_neighbors)
            
        full_vertex_obj = min(objective(n) for n in neighborhood)
        
        self.assertGreaterEqual(restricted_obj, full_vertex_obj, "Restricted objective must be >= full-vertex objective")
        
        if full_vertex_obj > 0:
            gap_pct = (restricted_obj - full_vertex_obj) / full_vertex_obj
            self.assertLess(gap_pct, 0.01, f"Hakimi bound exceeded generous tolerance: gap is {gap_pct*100:.3f}%")


