"""OptiLoc HK API — FastAPI app.

Endpoints:
  GET  /healthz             - liveness probe
  POST /solve_weber         - single-facility Weber (Weiszfeld) on HK demand
  POST /solve_kmedian_ozp   - k-median with OZP commercial constraint
  GET  /docs                - Swagger UI (public — DM artifact, Phase 1)
  GET  /redoc               - ReDoc (public)

Security posture (Session 014):
- Pydantic-bounded inputs (k, n_restarts within configured ranges).
- Per-IP rate limit via slowapi on solve_* endpoints.
- Per-request wall-clock timeout via asyncio.wait_for + thread offload.
- Global exception handler — generic 500 response, no stack-trace exposure.
- CORS open (no frontend yet; Session 018 will lock to landing-page origin).
- No auth — Phase 1 is a frictionless DM-demoable artifact.
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.responses import FileResponse

from api import __version__
from api.config import (
    KMEDIAN_TIMEOUT_S,
    RATE_LIMIT_SOLVE,
    ROAD_KMEDIAN_TIMEOUT_S,
    ROAD_WEBER_TIMEOUT_S,
    WEBER_TIMEOUT_S,
)
from api.competitor import run_competitor_coverage
from api.mclp import solve_mclp_road
from api.models import (
    AnalyzeNetworkRequest,
    AnalyzeNetworkResponse,
    CompetitorCoverageRequest,
    CompetitorCoverageResponse,
    HealthResponse,
    KMedianOZPRequest,
    KMedianOZPResponse,
    KMedianRoadRequest,
    KMedianRoadResponse,
    MCLPRoadRequest,
    MCLPRoadResponse,
    SolveKmedianRentRequest,
    SolveKmedianRentResponse,
    WeberResponse,
    WeberRoadResponse,
)
from api.rent_aware import solve_kmedian_rent_road
from api.solvers import analyze_network, initialize_solvers, solve_kmedian_ozp, solve_kmedian_road, solve_weber, solve_weber_road
import api.solvers as _solvers_cache

_NODE_TO_DISTRICT_PATH = Path(__file__).resolve().parent.parent / "data" / "rent" / "node_to_district.json"
_node_to_district: dict[str, str] = {}

logger = logging.getLogger("optiloc.api")
logging.basicConfig(level=logging.INFO)


# ---- Lifespan: load solvers + data at startup ---------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _node_to_district
    logger.info("Initializing solvers and loading data assets...")
    initialize_solvers()
    if _NODE_TO_DISTRICT_PATH.exists():
        with open(_NODE_TO_DISTRICT_PATH, encoding="utf-8") as fh:
            _node_to_district = json.load(fh)
        logger.info("Loaded node_to_district: %d entries", len(_node_to_district))
    else:
        logger.warning(
            "node_to_district.json not found at %s — "
            "/solve_kmedian_rent_road will be unavailable. "
            "Run scripts/precompute_districts.py to generate it.",
            _NODE_TO_DISTRICT_PATH,
        )
    logger.info("Startup complete.")
    yield
    logger.info("Shutting down.")


# ---- App + middleware ---------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="OptiLoc HK API",
    description=(
        "Hong Kong facility-location optimizer. Single-facility Weber "
        "(Weiszfeld) and multi-facility k-median with OZP commercial-zone "
        "constraint. Built on WorldPop 100m-grid demand and Lands Dept OZP "
        "zoning. github.com/Kaito-ishiguro/optiloc-hk"
    ),
    version=__version__,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

@app.get("/")
async def landing_page():
    return FileResponse("frontend/index.html")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Session 018 will lock to landing-page origin.
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---- Global exception handler -------------------------------------------------

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Log the real traceback server-side; return a generic message + a
    request_id the operator can grep for in logs. Prevents stack-trace
    or filesystem-path leakage to the client."""
    request_id = str(uuid.uuid4())
    logger.exception("Unhandled exception (request_id=%s): %s", request_id, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "request_id": request_id},
    )


# ---- Endpoints ----------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def healthz():
    """Liveness probe. Used by Docker HEALTHCHECK and Cloud Run."""
    return HealthResponse(status="ok", version=__version__)


@app.post(
    "/solve_weber",
    response_model=WeberResponse,
    tags=["optimize"],
    summary="Solve the single-facility Weber problem on Hong Kong demand.",
)
@limiter.limit(RATE_LIMIT_SOLVE)
async def post_solve_weber(request: Request):
    """
    Endpoint to solve the single-facility Weber problem using the Weiszfeld algorithm
    on Hong Kong demand data with Euclidean distances.
    """
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(solve_weber),
            timeout=WEBER_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Weber solver exceeded {WEBER_TIMEOUT_S}s timeout.",
        )
    return WeberResponse(**result)


@app.post(
    "/solve_kmedian_ozp",
    response_model=KMedianOZPResponse,
    tags=["optimize"],
    summary="Solve the k-median problem with OZP commercial-zone constraint.",
)
@limiter.limit(RATE_LIMIT_SOLVE)
async def post_solve_kmedian_ozp(request: Request, body: KMedianOZPRequest):
    """
    Endpoint to solve the k-median problem with an OZP commercial-zone constraint.
    Uses Lloyd's algorithm with population-weighted centroid snapping.
    """
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(solve_kmedian_ozp, body.k, body.n_restarts),
            timeout=KMEDIAN_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"k-median solver exceeded {KMEDIAN_TIMEOUT_S}s timeout.",
        )
    return KMedianOZPResponse(**result)


@app.post(
    "/solve_weber_road",
    response_model=WeberRoadResponse,
    tags=["optimize"],
    summary="Solve the single-facility Weber problem using HK road-network distances.",
)
@limiter.limit(RATE_LIMIT_SOLVE)
async def post_solve_weber_road(request: Request):
    """
    Endpoint to solve the single-facility Weber problem using road-network distances.
    Performs a multi-seed local search for the discrete road-network optimum.
    """
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(solve_weber_road),
            timeout=ROAD_WEBER_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Road Weber solver exceeded {ROAD_WEBER_TIMEOUT_S}s timeout.",
        )
    return WeberRoadResponse(**result)


@app.post(
    "/solve_kmedian_road",
    response_model=KMedianRoadResponse,
    tags=["optimize"],
    summary="Solve the k-median problem using HK road-network distances.",
)
@limiter.limit(RATE_LIMIT_SOLVE)
async def post_solve_kmedian_road(request: Request, body: KMedianRoadRequest):
    """
    Endpoint to solve the k-median problem using road-network distances.
    Uses a multi-start Lloyd's algorithm on the road graph.
    """
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(solve_kmedian_road, body.k, body.n_restarts),
            timeout=ROAD_KMEDIAN_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Road k-median solver exceeded {ROAD_KMEDIAN_TIMEOUT_S}s timeout.",
        )
    return KMedianRoadResponse(**result)

@app.post(
    "/analyze_network",
    response_model=AnalyzeNetworkResponse,
    tags=["optimize"],
    summary="Audit an existing facility network against the road-network k-median optimum.",
)
@limiter.limit(RATE_LIMIT_SOLVE)
async def post_analyze_network(request: Request, body: AnalyzeNetworkRequest):
    """
    Endpoint to audit an existing facility network against the road-network k-median optimum.
    Computes baseline metrics for existing locations and compares them to an optimal k-median solution.
    """
    k = body.k if body.k is not None else len(body.existing_locations)
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                analyze_network,
                body.existing_locations,
                k,
                body.n_restarts,
            ),
            timeout=ROAD_KMEDIAN_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"analyze_network exceeded {ROAD_KMEDIAN_TIMEOUT_S}s timeout.",
        )
    return AnalyzeNetworkResponse(**result)


@app.post(
    "/solve_mclp_road",
    response_model=MCLPRoadResponse,
    tags=["optimize"],
    summary="Maximise demand coverage within a road-network radius (binary or decay mode).",
)
@limiter.limit(RATE_LIMIT_SOLVE)
async def post_solve_mclp_road(request: Request, body: MCLPRoadRequest):
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                solve_mclp_road,
                body.k,
                body.r,
                body.lambda_m,
                body.n_restarts,
            ),
            timeout=ROAD_KMEDIAN_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"MCLP solver exceeded {ROAD_KMEDIAN_TIMEOUT_S}s timeout.",
        )
    return MCLPRoadResponse(**result)


@app.post(
    "/solve_kmedian_rent_road",
    response_model=SolveKmedianRentResponse,
    tags=["optimize"],
    summary="Rent-aware k-median: minimise a combined distance + industrial-rent objective.",
)
@limiter.limit(RATE_LIMIT_SOLVE)
async def post_solve_kmedian_rent_road(request: Request, body: SolveKmedianRentRequest):
    if not _node_to_district:
        raise HTTPException(
            status_code=503,
            detail=(
                "node_to_district.json not loaded. "
                "Run scripts/precompute_districts.py and redeploy."
            ),
        )
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                solve_kmedian_rent_road,
                _solvers_cache._road_graph,
                _solvers_cache._agg_demand_nodes,
                body.k,
                _node_to_district,
                body.rent_weight,
                body.facility_size_sqm,
                body.n_restarts,
            ),
            timeout=ROAD_KMEDIAN_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Rent-aware k-median exceeded {ROAD_KMEDIAN_TIMEOUT_S}s timeout.",
        )
    return SolveKmedianRentResponse(**result)


@app.post(
    "/competitor_coverage",
    response_model=CompetitorCoverageResponse,
    tags=["optimize"],
    summary="Differential coverage analysis: operator network vs competitor network.",
)
@limiter.limit(RATE_LIMIT_SOLVE)
async def post_competitor_coverage(request: Request, body: CompetitorCoverageRequest):
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                run_competitor_coverage,
                body.operator_locations,
                body.competitor_locations,
                body.threshold_m,
                body.recommend_site,
            ),
            timeout=ROAD_KMEDIAN_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Competitor coverage analysis exceeded {ROAD_KMEDIAN_TIMEOUT_S}s timeout.",
        )
    return CompetitorCoverageResponse(**result)