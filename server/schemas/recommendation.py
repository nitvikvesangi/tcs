from pydantic import BaseModel
from typing import List, Optional

class PromotionOption(BaseModel):
    discount_pct: float
    expected_sales_units: int
    expected_revenue: float
    expected_profit: float
    profit_impact_pct: float
    inventory_reduction_pct: float
    stockout_risk_pct: float
    expiry_waste_reduction_pct: float
    score: float

class InventorySnapshot(BaseModel):
    stockout_urgency: str
    overstock_urgency: str
    expiry_urgency: str
    inventory_alert_score: float

class RecommendationDecision(BaseModel):
    action: str
    discount_pct: float
    objective: str

class RecommendationResponse(BaseModel):
    product_id: str
    dark_store_id: str
    
    # Core AI Contract
    recommendation: RecommendationDecision
    reasons: List[str]
    risk_flag: str
    options: List[PromotionOption]
    inventory_snapshot: InventorySnapshot

    # Hyperlocal Context
    product_name: str
    category: str
    city: str
    current_stock: int
    days_to_expiry: int
    demand_status: str
    demand_trend_pct: float
    trend_signal: Optional[str] = None
    weather_condition: Optional[str] = None
    time_of_day: Optional[str] = None
    is_weekend: Optional[bool] = None
    gross_margin_before_promo: Optional[float] = None
    competitor_price_gap_pct: Optional[float] = None
    stockout_risk_pct: float
