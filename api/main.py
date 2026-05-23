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
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api import __version__
from api.config import (
    KMEDIAN_TIMEOUT_S,
    RATE_LIMIT_SOLVE,
    WEBER_TIMEOUT_S,
)
from api.models import (
    HealthResponse,
    KMedianOZPRequest,
    KMedianOZPResponse,
    WeberResponse,
)
from api.solvers import initialize_solvers, solve_kmedian_ozp, solve_weber

logger = logging.getLogger("optiloc.api")
logging.basicConfig(level=logging.INFO)


# ---- Lifespan: load solvers + data at startup ---------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing solvers and loading data assets...")
    initialize_solvers()
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
)

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

@app.get("/healthz", response_model=HealthResponse, tags=["meta"])
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
