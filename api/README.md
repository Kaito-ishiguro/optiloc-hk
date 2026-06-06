# OptiLoc HK API Endpoints

This module exposes FastAPI endpoints for solving facility location problems on the Hong Kong road network and Euclidean space. The solvers use population-weighted demand nodes, with constraints available for commercial zones.

## Available Endpoints

### 1. `GET /health`
Liveness probe used for container orchestration and health checks.
* **Returns**: A basic status object (`{"status": "ok", "version": "..."}`).

### 2. `POST /solve_weber`
Solves the single-facility Weber problem (1-median) using Euclidean distances.
* **Algorithm**: Weiszfeld algorithm starting from a baked-in Victoria Harbour location.
* **Returns**: The optimal longitude and latitude, the objective value (total weighted distance in degree-units), solver iterations, and runtime metrics.

### 3. `POST /solve_kmedian_ozp`
Solves the multi-facility k-median problem constrained to Outline Zoning Plan (OZP) commercial zones.
* **Algorithm**: Lloyd's algorithm over multiple random initializations using Euclidean distances and population-weighted centroid snapping.
* **Body**: `{"k": int, "n_restarts": int}`
* **Returns**: The best objective found, the worst objective found, the objective gap percentage, and a list of recommended facility coordinates alongside statistics for each restart.

### 4. `POST /solve_weber_road`
Solves the single-facility Weber problem using the actual Hong Kong road network.
* **Algorithm**: A discrete local search over the road network graph using 3 diverse seed nodes.
* **Returns**: The optimal road node ID, its coordinates, the total weighted road distance (in metres), the average distance per resident (m/resident), and runtime statistics.

### 5. `POST /solve_kmedian_road`
Solves the k-median problem using the Hong Kong road network.
* **Algorithm**: A multi-start Lloyd's algorithm on the road graph (assignment via Dijkstra shortest paths, location via population-weighted centroid snapping to nearest road nodes).
* **Body**: `{"k": int, "n_restarts": int}`
* **Returns**: The best objective (metres), per-resident distance, worst objective, and the recommended facilities including node IDs, coordinates, and total population served.

### 6. `POST /analyze_network`
Audits an existing facility network against the road-network k-median optimum.
* **Algorithm**: Computes the baseline objective for a set of provided locations, then runs the road-network k-median solver to find an optimal benchmark.
* **Body**: `{"existing_locations": [[lat, lon], ...], "k": int, "n_restarts": int}`
* **Returns**: The baseline and optimal objectives, the percentage improvement achievable, the baseline and optimal per-resident distances, and the optimal facility locations.
