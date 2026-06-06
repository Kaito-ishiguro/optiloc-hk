"""Pydantic request/response schemas for the OptiLoc API.

All numeric inputs are bounded via Pydantic Field constraints to prevent DoS
via pathological values (e.g. k=1_000_000).
"""

from typing import Dict, List, Optional

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

# ---- /solve_weber_road --------------------------------------------------------

class WeberRoadResponse(BaseModel):
    node_id: int = Field(..., description="Road graph node ID of the optimum.")
    lon: float = Field(..., description="Optimum longitude (WGS84).")
    lat: float = Field(..., description="Optimum latitude (WGS84).")
    objective: float = Field(..., description="Total weighted road distance (metres).")
    per_resident_m: float = Field(..., description="Objective / total population (m/resident).")
    runtime_s: float
    n_demand_nodes: int
    total_weight: float


# ---- /solve_kmedian_road ------------------------------------------------------

class KMedianRoadRequest(BaseModel):
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


class RoadFacility(BaseModel):
    node_id: int
    lon: float
    lat: float
    population_served: float
    pct_served: float


class KMedianRoadResponse(BaseModel):
    k: int
    n_restarts: int
    best_objective: float = Field(..., description="Best total weighted road distance (metres).")
    per_resident_m: float
    worst_objective: float
    worst_best_gap_pct: float
    n_distinct_optima: int
    facilities: list[RoadFacility]
    runtime_s: float
    n_demand_nodes: int
    total_weight: float

    
# ---- /analyze_network ---------------------------------------------------------

class AnalyzeNetworkRequest(BaseModel):
    existing_locations: list[tuple[float, float]] = Field(
        ...,
        min_length=1,
        max_length=MAX_K,
        description="List of (lat, lon) pairs for existing facilities.",
    )
    k: int | None = Field(
        None,
        ge=MIN_K,
        le=MAX_K,
        description="Number of optimal facilities to solve for. Defaults to len(existing_locations).",
    )
    n_restarts: int = Field(
        DEFAULT_RESTARTS,
        ge=MIN_RESTARTS,
        le=MAX_RESTARTS,
        description=f"Multi-start count for k-median solver ({MIN_RESTARTS}-{MAX_RESTARTS}).",
    )


class AnalyzeNetworkResponse(BaseModel):
    k: int
    baseline_objective: float = Field(..., description="Total weighted road distance for existing locations (metres).")
    optimal_objective: float = Field(..., description="Total weighted road distance for optimised locations (metres).")
    improvement_pct: float = Field(..., description="Percentage improvement: (baseline - optimal) / baseline * 100.")
    baseline_per_resident_m: float
    optimal_per_resident_m: float
    recommended_facilities: list[RoadFacility]
    runtime_s: float
    n_demand_nodes: int
    total_weight: float


# ---- /solve_mclp_road ---------------------------------------------------------

class MCLPRoadRequest(BaseModel):
    k: int = Field(
        DEFAULT_K,
        ge=MIN_K,
        le=MAX_K,
        description=f"Number of facilities to open ({MIN_K}-{MAX_K}).",
    )
    r: float = Field(
        3000.0,
        ge=500.0,
        le=10_000.0,
        description="Coverage radius in metres (500-10 000). Default 3 000 m.",
    )
    lambda_m: float | None = Field(
        None,
        ge=100.0,
        le=50_000.0,
        description=(
            "Decay constant in metres for exponential coverage credit "
            "exp(-d / lambda_m). None → binary mode (covered or not)."
        ),
    )
    n_restarts: int = Field(
        5,
        ge=MIN_RESTARTS,
        le=MAX_RESTARTS,
        description=f"Multi-start count ({MIN_RESTARTS}-{MAX_RESTARTS}). Default 5.",
    )


class MCLPFacility(BaseModel):
    node_id: int = Field(..., description="Road graph node ID.")
    lon: float = Field(..., description="Facility longitude (WGS84).")
    lat: float = Field(..., description="Facility latitude (WGS84).")


class MCLPRoadResponse(BaseModel):
    k: int
    r: float = Field(..., description="Coverage radius used (metres).")
    lambda_m: float | None = Field(
        ..., description="Decay constant (metres); null in binary mode."
    )
    n_restarts: int
    objective: float = Field(
        ...,
        description=(
            "Best objective found. Binary mode: total covered demand weight. "
            "Decay mode: sum(weight * exp(-dist / lambda_m))."
        ),
    )
    coverage_pct: float = Field(
        ...,
        description=(
            "Percentage of total weighted demand within r metres of the "
            "nearest open facility (binary formula, both modes)."
        ),
    )
    facilities: list[MCLPFacility]
    runtime_s: float
    n_demand_nodes: int
    total_weight: float


# ---- /solve_kmedian_rent_road -------------------------------------------------

class RentBreakdownItem(BaseModel):
    district: str
    region: str | None = Field(..., description="RVD macro-region; null for excluded districts.")
    rent_hkd_sqm_month: int = Field(..., description="HK$/sqm/month (Q4 2025 RVD flatted factories).")
    monthly_cost_hkd: int = Field(..., description="Monthly rent for the facility (rent × facility_size_sqm).")


class SolveKmedianRentRequest(BaseModel):
    k: int = Field(
        DEFAULT_K,
        ge=MIN_K,
        le=MAX_K,
        description=f"Number of facilities ({MIN_K}-{MAX_K}).",
    )
    rent_weight: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description=(
            "Trade-off weight for rent penalty (0 = pure distance, "
            "1 = equal weight on distance and normalised rent). Default 0."
        ),
    )
    facility_size_sqm: int = Field(
        500,
        ge=1,
        le=100_000,
        description="Assumed facility floor area in m², used only for monthly cost reporting. Default 500.",
    )
    n_restarts: int = Field(
        5,
        ge=MIN_RESTARTS,
        le=MAX_RESTARTS,
        description=f"Multi-start count ({MIN_RESTARTS}-{MAX_RESTARTS}). Default 5.",
    )
    existing_locations: list[tuple[float, float]] | None = Field(
        None,
        description="Optional list of (lat, lon) pairs for existing facilities (unused by solver; reserved).",
    )


class RentFacility(BaseModel):
    node_id: int = Field(..., description="Road graph node ID.")
    lon: float = Field(..., description="Facility longitude (WGS84).")
    lat: float = Field(..., description="Facility latitude (WGS84).")


class SolveKmedianRentResponse(BaseModel):
    facilities: list[RentFacility]
    mean_distance_m: float = Field(..., description="Population-weighted mean road distance at the optimum (metres).")
    improvement_pct: float = Field(
        ...,
        description="Improvement in mean_distance_m from worst to best restart (%).",
    )
    rent_breakdown: list[RentBreakdownItem]
    total_monthly_rent_hkd: float = Field(..., description="Total monthly rent across all facilities (HK$).")
    rent_weight_used: float
    runtime_s: float
    n_demand_nodes: int
    total_weight: float


# ---- /competitor_coverage -----------------------------------------------------

class CompetitorCoverageRequest(BaseModel):
    operator_locations: List[List[float]] = Field(
        ...,
        min_length=1,
        description="Operator facility coordinates as [[lat, lng], ...].",
    )
    competitor_locations: List[List[float]] = Field(
        ...,
        min_length=1,
        description="Competitor facility coordinates as [[lat, lng], ...].",
    )
    threshold_m: float = Field(
        3000.0,
        ge=500.0,
        le=20_000.0,
        description="Coverage radius in metres for 'covered' classification. Default 3 000 m.",
    )
    recommend_site: bool = Field(
        True,
        description="If true, run at-risk 1-median to recommend a new site. Default true.",
    )


class ZoneStats(BaseModel):
    demand_pct: float = Field(..., description="Percentage of total weighted demand in this zone.")
    resident_count: int = Field(..., description="Estimated resident count in this zone.")


class CompetitorCoverageResponse(BaseModel):
    at_risk_demand_pct: float = Field(
        ...,
        description="Percentage of weighted demand where competitor is closer (competitor_wins zone).",
    )
    at_risk_resident_count: int = Field(
        ...,
        description="Estimated resident count in the competitor_wins zone.",
    )
    operator_mean_distance_m: float = Field(
        ...,
        description="Population-weighted mean road distance from operator network over all demand.",
    )
    competitor_mean_distance_m: float = Field(
        ...,
        description="Population-weighted mean road distance from competitor network over all demand.",
    )
    zones: Dict[str, ZoneStats] = Field(
        ...,
        description="Per-zone demand stats: operator_wins, competitor_wins, neither.",
    )
    recommended_site: Optional[Dict] = Field(
        None,
        description=(
            "Recommended new site targeting at-risk demand: node_id, lat, lng, "
            "at_risk_mean_distance_m. Null if recommend_site=false or no at-risk demand."
        ),
    )