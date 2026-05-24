"""Security limits, paths, and runtime constants for the OptiLoc API.

These values bound resource usage on the public endpoints (per Session 014
security review). Tune as customer-discovery surfaces real workload patterns.
"""

from pathlib import Path

# Repo root is two levels up from this file (api/config.py).
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "processed"
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"

# Data assets baked into the container at build time.
DEMAND_CSV = DATA_DIR / "demand_points.csv"
OZP_GEOJSON = DATA_DIR / "ozp_commercial_union.geojson"

# Numbered solver scripts, loaded via importlib.util (file names start with digits).
WEBER_SOLVER_PATH = NOTEBOOKS_DIR / "08_solve_weber_weiszfeld.py"
KMEDIAN_SOLVER_PATH = NOTEBOOKS_DIR / "16_solve_kmedian_ozp.py"

# Road-network data assets baked into the container.
ROAD_GRAPH_ML = DATA_DIR / "hk_road_network.graphml"
ROAD_AGG_CSV  = DATA_DIR / "demand_nodes_aggregated.csv"

# Road-network solver limits and timeouts.
ROAD_WEBER_TIMEOUT_S   = 120
ROAD_KMEDIAN_TIMEOUT_S = 300
ROAD_KMEDIAN_MAX_ITERS = 15   # Lloyd iterations per restart (matches notebook 23).

# ---- Security / DoS limits ----------------------------------------------------

MAX_K = 25                # Largest k-median problem size we'll accept.
MIN_K = 2
MAX_RESTARTS = 20
MIN_RESTARTS = 1

RATE_LIMIT_SOLVE = "5/minute"   # Per-IP, applied to /solve_* endpoints.

# Wall-clock timeouts (seconds). Defense-in-depth on top of Cloud Run's own
# request timeout. Weber is ~10ms; k-median is ~107s at k=5/10 restarts
# per Session 012, so the k-median ceiling is generous.
WEBER_TIMEOUT_S = 30
KMEDIAN_TIMEOUT_S = 180

# ---- Solver defaults ----------------------------------------------------------

DEFAULT_K = 5
DEFAULT_RESTARTS = 10
WEISZFELD_START_LON = 114.17
WEISZFELD_START_LAT = 22.32
BUFFER_DEG = 1e-6         # Session 010b SLSQP smoothness fix.
RNG_SEED = 42             # Reproducibility with Session 012 / 013 outputs.
