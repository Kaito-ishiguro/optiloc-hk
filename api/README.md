# OptiLoc HK API Endpoints

This module exposes FastAPI endpoints for solving facility location problems on the Hong Kong road network and Euclidean space. The solvers use population-weighted demand nodes, with constraints available for commercial zones.

## Available Endpoints

### 1. `GET /health`
Liveness probe used for container orchestration and health checks.
* **Returns**: A basic status object (`{"status": "str", "version": "str"}`).

### 2. `POST /solve_weber`
Solves the single-facility Weber problem (1-median) using Euclidean distances.
* **Algorithm**: Weiszfeld algorithm starting from a baked-in Victoria Harbour location.
* **Body**: Empty body.
* **Returns**: The optimal `lon` and `lat`, the `objective` value (total weighted distance in degree-units), solver `iterations`, `runtime_s`, `n_demand_points`, and `total_weight`.

### 3. `POST /solve_kmedian_ozp`
Solves the multi-facility k-median problem constrained to Outline Zoning Plan (OZP) commercial zones.
* **Algorithm**: Lloyd's algorithm over multiple random initializations using Euclidean distances and population-weighted centroid snapping.
* **Body**: `{"k": int, "n_restarts": int}`
* **Returns**: `k`, `n_restarts`, `best_objective`, `worst_objective`, `worst_best_gap_pct`, `n_distinct_optima`, `facilities` (list of `{"lon": float, "lat": float}`), `restarts` (list of statistics), and `runtime_s`.

### 4. `POST /solve_weber_road`
Solves the single-facility Weber problem using the actual Hong Kong road network.
* **Algorithm**: A discrete local search over the road network graph using 3 diverse seed nodes.
* **Body**: Empty body.
* **Returns**: The optimal `node_id`, `lon`, `lat`, the `objective` (metres), `per_resident_m`, `runtime_s`, `n_demand_nodes`, and `total_weight`.

### 5. `POST /solve_kmedian_road`
Solves the k-median problem using the Hong Kong road network.
* **Algorithm**: A multi-start Lloyd's algorithm on the road graph (assignment via Dijkstra shortest paths, location via population-weighted centroid snapping to nearest road nodes) with a post-Lloyd Maranzana local search refinement.
* **Body**: `{"k": int, "n_restarts": int}`
* **Returns**: `k`, `n_restarts`, `best_objective` (metres), `per_resident_m`, `worst_objective`, `worst_best_gap_pct`, `n_distinct_optima`, `facilities` (list of `{"node_id": int, "lon": float, "lat": float, "population_served": float, "pct_served": float}`), `runtime_s`, `n_demand_nodes`, and `total_weight`.

### 6. `POST /analyze_network`
Audits an existing facility network against the road-network k-median optimum.
* **Algorithm**: Computes the baseline objective for a set of provided locations, then runs the road-network k-median solver to find an optimal benchmark.
* **Body**: `{"existing_locations": list[tuple[float, float]], "k": int | None, "n_restarts": int}`
* **Returns**: `k`, `baseline_objective`, `optimal_objective`, `improvement_pct`, `baseline_per_resident_m`, `optimal_per_resident_m`, `recommended_facilities` (list of road facilities), `runtime_s`, `n_demand_nodes`, and `total_weight`.

### 7. `POST /solve_mclp_road`
Solves the Maximal Coverage Location Problem (MCLP) on the Hong Kong road network.
* **Algorithm**: Greedy interchange heuristic to maximize demand covered within a service radius, capturing binary coverage boundaries or continuous distance decay.
* **Body**: `{"k": int, "r": float, "lambda_m": float | None, "n_restarts": int}`
* **Returns**: `k`, `r`, `lambda_m`, `n_restarts`, `objective`, `coverage_pct`, `facilities` (list of `{"node_id": int, "lon": float, "lat": float}`), `runtime_s`, `n_demand_nodes`, and `total_weight`.

### 8. `POST /solve_kmedian_rent_road`
Solves a rent-aware k-median problem trading off road distance against regional rent penalties.
* **Algorithm**: Multi-start Lloyd's algorithm with low-rent seeding bias, centroid snapping, and a post-Lloyd Maranzana local search refinement. Selects the best restart by combined distance and rent penalty objective.
* **Body**: `{"k": int, "rent_weight": float, "facility_size_sqm": int, "n_restarts": int, "existing_locations": list[tuple[float, float]] | None}`
* **Returns**: `facilities` (list of `{"node_id": int, "lon": float, "lat": float}`), `mean_distance_m`, `improvement_pct`, `rent_breakdown` (list of `{"district": str, "region": str | None, "rent_hkd_sqm_month": int, "monthly_cost_hkd": int}`), `total_monthly_rent_hkd`, `rent_weight_used`, `runtime_s`, `n_demand_nodes`, and `total_weight`.

### 9. `POST /competitor_coverage`
Classifies demand nodes against competitor networks to isolate at-risk zones.
* **Algorithm**: Multi-source Dijkstra to classify demand zones, optionally followed by an at-risk 1-median solver to recommend a new site.
* **Body**: `{"operator_locations": list[list[float]], "competitor_locations": list[list[float]], "threshold_m": float, "recommend_site": bool}`
* **Returns**: `at_risk_demand_pct`, `at_risk_resident_count`, `operator_mean_distance_m`, `competitor_mean_distance_m`, `zones` (dict of `{"demand_pct": float, "resident_count": int}`), and `recommended_site` (dict | None).
