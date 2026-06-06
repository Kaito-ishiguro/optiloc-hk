import unittest

from api import solvers

# Initialize solvers at module load time for tests
solvers.initialize_solvers()


class TestSolvers(unittest.TestCase):

    def test_multi_seed_best_of_selection(self):
        """
        Invariant 3: Multi-seed best-of selection correctness.
        Asserts that the best_objective returned is less than or equal to 
        every individual restart's objective in the sweep.
        """
        k = 2
        n_restarts = 5
        result = solvers.solve_kmedian_ozp(k=k, n_restarts=n_restarts)
        
        best_obj = result["best_objective"]
        
        for r in result["restarts"]:
            self.assertLessEqual(best_obj, r["final_obj"], "Best objective is not <= a restart's objective")


    def test_baseline_headline_stat_true_median(self):
        """
        Invariant 4: Single-seed deterministic regression guard for the k=2
        true-median (Maranzana) result on the production graph (18,820 nodes).

        Prior value (centroid-snap only):
          9014.92465115422 m/resident — the old published '42.97%' headline.
          Source: benchmarks/centroid_vs_median.py, N_RESTARTS=5, 12,513-node graph.

        Current value (post-Lloyd Maranzana refinement, production switch Session 046):
          8603.946 m/resident — corresponds to ~46% improvement vs the same baseline.
          Deterministic under RNG_SEED=42 with n_restarts=1: same Lloyd warm start
          each time, same Maranzana hill-climb path from that warm start.

        This test calls solve_kmedian_road with n_restarts=1 (single-seed,
        deterministic under RNG_SEED=42). The 18,820-node production graph is
        verified first.
        """
        # 1. Assert we are using the correct production graph snapshot (18,820 nodes)
        expected_node_count = 18820
        actual_node_count = len(solvers._road_graph.nodes())
        self.assertEqual(actual_node_count, expected_node_count,
                         f"Expected {expected_node_count} graph nodes, got {actual_node_count}")

        # 2. Run k=2 true-median solver, single seed (deterministic under RNG_SEED=42)
        result = solvers.solve_kmedian_road(k=2, n_restarts=1)

        # 3. Assert the post-Maranzana value (must be strictly better than old 9014.924)
        expected_per_resident = 8603.946
        actual_per_resident = result["per_resident_m"]

        self.assertTrue(
            abs(actual_per_resident - expected_per_resident) < 0.1,
            f"True-median regression: expected ~{expected_per_resident}, got {actual_per_resident}"
        )

