"""
Analytics Pydantic schemas.

These schemas define the response contracts for Phase 3 analytics endpoints.
They are declared here in Phase 1 so that:
  - The full API surface is visible in Swagger from Phase 1 onward.
  - Phase 3 service layer can be implemented against a stable contract.
  - Frontend can mock against these types immediately.
"""

import datetime
from typing import List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Sales analytics
# ---------------------------------------------------------------------------

class SalesDataPoint(BaseModel):
    date: datetime.date
    units_sold: int
    revenue: float
    profit: float


class SalesTrendResponse(BaseModel):
    store_id: Optional[int]
    product_id: Optional[int]
    period_days: int
    data_points: List[SalesDataPoint]


# ---------------------------------------------------------------------------
# Demand forecast
# ---------------------------------------------------------------------------

class DemandForecastPoint(BaseModel):
    date: datetime.date
    predicted_units: float
    lower_bound: float
    upper_bound: float


class DemandForecastResponse(BaseModel):
    product_id: int
    store_id: int
    forecast_days: int
    forecast: List[DemandForecastPoint]


# ---------------------------------------------------------------------------
# Customer analytics
# ---------------------------------------------------------------------------

class CustomerAnalyticsResponse(BaseModel):
    store_id: Optional[int]
    period_days: int
    total_views: int
    total_searches: int
    total_cart_adds: int
    total_purchases: int
    # purchases / views — 0 if no views
    view_to_purchase_rate: float
    # purchases / cart_adds — 0 if no cart adds
    cart_to_purchase_rate: float
    repeat_purchase_rate: float


# ---------------------------------------------------------------------------
# Trend / product analytics
# ---------------------------------------------------------------------------

class ProductTrendPoint(BaseModel):
    product_id: int
    product_sku: str
    product_name: str
    trend_score: float
    demand_trend: str
    sales_velocity: Optional[float]


class TrendsResponse(BaseModel):
    store_id: Optional[int]
    date: datetime.date
    trending_products: List[ProductTrendPoint]


# ---------------------------------------------------------------------------
# Store comparison
# ---------------------------------------------------------------------------

class StoreMetrics(BaseModel):
    store_id: int
    store_code: str
    store_city: str
    total_revenue: float
    total_profit: float
    units_sold: int
    active_promotions: int
    inventory_alert_count: int


class StoreComparisonResponse(BaseModel):
    period_days: int
    stores: List[StoreMetrics]
