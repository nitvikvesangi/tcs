"""
Simulation Pydantic schemas.

Used by POST /api/v1/promotions/simulate and /compare endpoints (Phase 4).
Declared here so the API contract is stable before the engine is built.
"""

from typing import List

from pydantic import BaseModel, Field


class SimulationResult(BaseModel):
    """
    Result of simulating a single (product, store, discount_pct) scenario.

    All values are deterministic — the Promotion Engine uses no random numbers.
    """
    discount_pct: float
    expected_sales_units: float
    expected_revenue: float
    expected_profit: float
    inventory_reduction_pct: float
    stockout_risk_pct: float
    expiry_waste_reduction_pct: float
    profit_impact_pct: float


class SimulationResponse(BaseModel):
    product_id: int
    dark_store_id: int
    duration_days: int
    result: SimulationResult


class ComparisonResponse(BaseModel):
    """
    Side-by-side comparison of multiple discount scenarios.

    Each option in `results` corresponds to one discount_pct from the request.
    """
    product_id: int
    dark_store_id: int
    duration_days: int
    results: List[SimulationResult] = Field(min_length=2)
