"""Pydantic request/response schemas for the OptiLoc API.

All numeric inputs are bounded via Pydantic Field constraints to prevent DoS
via pathological values (e.g. k=1_000_000).
"""

from pydantic import BaseModel, Field

from api.config import (
    DEFAULT_K,
    DEFAULT_RESTARTS,
    MAX_K,
    MAX_RESTARTS,
    MIN_K,
    MIN_RESTARTS,
)


# ---- /healthz -----------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


# ---- /solve_weber -------------------------------------------------------------

class WeberRequest(BaseModel):
    """Empty body for Session 014. Session 015+ will accept a caller-supplied
    start point and tolerance."""
    pass


class WeberResponse(BaseModel):
    lon: float = Field(..., description="Optimum longitude (WGS84).")
    lat: float = Field(..., description="Optimum latitude (WGS84).")
    objective: float = Field(
        ..., description="Total weighted distance at the optimum (degree-units)."
    )
    iterations: int
    runtime_s: float
    n_demand_points: int
    total_weight: float


# ---- /solve_kmedian_ozp -------------------------------------------------------

class KMedianOZPRequest(BaseModel):
    k: int = Field(
        DEFAULT_K,
        ge=MIN_K,
        le=MAX_K,
        description=f"Number of facilities ({MIN_K}-{MAX_K}).",
    )
    n_restarts: int = Field(
        DEFAULT_RESTARTS,
        ge=MIN_RESTARTS,
        le=MAX_RESTARTS,
        description=f"Multi-start count ({MIN_RESTARTS}-{MAX_RESTARTS}).",
    )


class Facility(BaseModel):
    lon: float
    lat: float


class RestartSummary(BaseModel):
    restart_id: int
    final_obj: float
    n_lloyd_iters: int
    converged: bool
    slsqp_calls: int
    weiszfeld_calls: int


class KMedianOZPResponse(BaseModel):
    k: int
    n_restarts: int
    best_objective: float
    worst_objective: float
    worst_best_gap_pct: float
    n_distinct_optima: int
    facilities: list[Facility]
    restarts: list[RestartSummary]
    runtime_s: float
