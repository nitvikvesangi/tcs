"""
Promotion Pydantic schemas.

The PromotionRecommendationResponse schema is the primary API contract for
the Promotion Engine (Phase 4).  Its structure is fixed here so that:
  - The chatbot (Phase 5) can rely on a stable schema when reading stored
    `recommendation_data` JSON from the Promotion model.
  - Frontend can develop against the contract before Phase 4 ships.
  - The schema test in Phase 1 locks the contract against accidental change.

Exact contract preserved per project specification:

  {
    "product_id": "P0059",
    "dark_store_id": "BEN-DS4",
    "recommended_action": "CLEARANCE",
    "discount_pct": 25,
    "reasons": ["expiry_urgency=Critical (0 days left of 1-day shelf life)"],
    "risk_flag": "EXPIRY_CRITICAL",
    "options": [
      { "discount_pct": 25, "expected_profit": 47.6,
        "inventory_reduction_pct": 12.4, "stockout_risk_pct": 15.6,
        "score": 47.63 },
      ...
    ],
    "inventory_snapshot": {
      "stockout_urgency": "High",
      "overstock_urgency": "Critical",
      "expiry_urgency": "Critical",
      "inventory_alert_score": 100
    }
  }
"""

import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.utils.enums import (
    PromotionObjective,
    PromotionStatus,
    PromotionType,
    RiskFlag,
)


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class PromotionOption(BaseModel):
    """
    A single candidate offer produced by the Promotion Engine.

    The engine always generates 2–3 of these; the retailer selects one.
    """
    discount_pct: float = Field(ge=0, le=100, description="Discount percentage")
    expected_profit: float = Field(description="Expected profit in INR (may be negative)")
    inventory_reduction_pct: float = Field(
        ge=0, description="Expected % reduction of current stock"
    )
    stockout_risk_pct: float = Field(ge=0, le=100, description="Probability of stockout (%)")
    score: float = Field(description="Objective-weighted score; higher is better")


class InventorySnapshot(BaseModel):
    """
    Current urgency summary for the product at the requested store.

    Urgency strings use title-case display values matching the project contract
    ("High", "Critical") rather than enum uppercase ("HIGH", "CRITICAL").
    The Inventory Engine (Phase 2) populates these.
    """
    stockout_urgency: str = Field(description="LOW | MEDIUM | HIGH | CRITICAL (display)")
    overstock_urgency: str = Field(description="LOW | MEDIUM | HIGH | CRITICAL (display)")
    expiry_urgency: str = Field(description="LOW | MEDIUM | HIGH | CRITICAL (display)")
    inventory_alert_score: int = Field(ge=0, le=100, description="Composite urgency 0–100")


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class PromotionRecommendRequest(BaseModel):
    """Body for POST /api/v1/promotions/recommend."""
    product_id: int
    dark_store_id: int
    objective: PromotionObjective = PromotionObjective.BALANCED
    max_discount_pct: float = Field(default=50.0, ge=0, le=100)
    min_margin_pct: float = Field(default=0.0, ge=-100, le=100)
    budget: Optional[float] = Field(default=None, gt=0, description="Max promo spend in INR")


class PromotionSimulateRequest(BaseModel):
    """Body for POST /api/v1/promotions/simulate — single scenario."""
    product_id: int
    dark_store_id: int
    discount_pct: float = Field(ge=0, le=100)
    duration_days: int = Field(default=7, ge=1, le=90)


class PromotionCompareRequest(BaseModel):
    """Body for POST /api/v1/promotions/compare — compare N discount levels."""
    product_id: int
    dark_store_id: int
    discount_pcts: List[float] = Field(min_length=2, max_length=5)
    duration_days: int = Field(default=7, ge=1, le=90)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class MLPrediction(BaseModel):
    """Output from the RandomForest ML model."""
    action: str
    confidence: float
    probabilities: Dict[str, float] = {}
    model_type: str = "RandomForestClassifier"
    features_used: int = 0
    fallback_used: bool = False


class PromotionRecommendationResponse(BaseModel):
    """
    Full promotion recommendation response.

    `product_id` and `dark_store_id` are string identifiers (e.g. SKU, store code)
    to match the project JSON contract ("P0059", "BEN-DS4").
    """
    product_id: str
    dark_store_id: str
    recommended_action: str = Field(description="CLEARANCE | PERCENTAGE_DISCOUNT | etc.")
    discount_pct: float
    reasons: List[str]
    risk_flag: str = Field(description="RiskFlag value, e.g. EXPIRY_CRITICAL")
    options: List[PromotionOption]
    inventory_snapshot: InventorySnapshot
    ml_prediction: Optional[MLPrediction] = Field(default=None, description="RandomForest ML model prediction")
    ai_explanation: Optional[str] = Field(default=None, description="LLM-generated explanation")

    model_config = {"json_schema_extra": {"example": {
        "product_id": "P0059",
        "dark_store_id": "BEN-DS4",
        "recommended_action": "CLEARANCE",
        "discount_pct": 25,
        "reasons": ["expiry_urgency=Critical (0 days left of 1-day shelf life)"],
        "risk_flag": "EXPIRY_CRITICAL",
        "options": [
            {
                "discount_pct": 25,
                "expected_profit": 47.6,
                "inventory_reduction_pct": 12.4,
                "stockout_risk_pct": 15.6,
                "score": 47.63,
            },
            {
                "discount_pct": 35,
                "expected_profit": 10.0,
                "inventory_reduction_pct": 13.6,
                "stockout_risk_pct": 16.1,
                "score": 10.04,
            },
            {
                "discount_pct": 45,
                "expected_profit": -32.5,
                "inventory_reduction_pct": 14.4,
                "stockout_risk_pct": 16.6,
                "score": -32.52,
            },
        ],
        "inventory_snapshot": {
            "stockout_urgency": "High",
            "overstock_urgency": "Critical",
            "expiry_urgency": "Critical",
            "inventory_alert_score": 100,
        },
    }}}


class PromotionHistoryItem(BaseModel):
    """Single item in GET /api/v1/promotions/history."""
    id: int
    product_id: int
    dark_store_id: int
    promotion_type: PromotionType
    objective: PromotionObjective
    status: PromotionStatus
    discount_pct: float
    risk_flag: RiskFlag
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class PromotionApproveRequest(BaseModel):
    """Body for POST /api/v1/promotions/{id}/approve."""
    selected_discount_pct: float = Field(ge=0, le=100)
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    notes: Optional[str] = None
