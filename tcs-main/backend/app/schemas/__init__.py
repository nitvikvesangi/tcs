"""
Schemas package — re-exports all public schema classes.

Import from here rather than from individual submodules for a stable surface:

  from app.schemas import UserOut, PromotionRecommendationResponse
"""

from app.schemas.auth import LoginRequest, TokenResponse, UserOut, UserRegisterRequest
from app.schemas.retailer import RetailerCreate, RetailerOut
from app.schemas.store import DarkStoreCreate, DarkStoreOut, DarkStoreSummary
from app.schemas.product import ProductCreate, ProductOut, ProductSummary
from app.schemas.inventory import InventoryOut, InventoryUpdate, InventoryWithProductOut
from app.schemas.analytics import (
    CustomerAnalyticsResponse,
    DemandForecastResponse,
    ProductTrendPoint,
    SalesTrendResponse,
    StoreComparisonResponse,
    TrendsResponse,
)
from app.schemas.promotion import (
    InventorySnapshot,
    PromotionApproveRequest,
    PromotionCompareRequest,
    PromotionHistoryItem,
    PromotionOption,
    PromotionRecommendationResponse,
    PromotionRecommendRequest,
    PromotionSimulateRequest,
)
from app.schemas.simulation import ComparisonResponse, SimulationResponse, SimulationResult
from app.schemas.alerts import AlertsResponse, InventoryAlert
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse, ToolCallRecord

__all__ = [
    # auth
    "UserRegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserOut",
    # retailer
    "RetailerCreate",
    "RetailerOut",
    # store
    "DarkStoreCreate",
    "DarkStoreSummary",
    "DarkStoreOut",
    # product
    "ProductCreate",
    "ProductSummary",
    "ProductOut",
    # inventory
    "InventoryOut",
    "InventoryUpdate",
    "InventoryWithProductOut",
    # analytics
    "SalesTrendResponse",
    "DemandForecastResponse",
    "CustomerAnalyticsResponse",
    "TrendsResponse",
    "ProductTrendPoint",
    "StoreComparisonResponse",
    # promotion
    "PromotionOption",
    "InventorySnapshot",
    "PromotionRecommendRequest",
    "PromotionSimulateRequest",
    "PromotionCompareRequest",
    "PromotionRecommendationResponse",
    "PromotionHistoryItem",
    "PromotionApproveRequest",
    # simulation
    "SimulationResult",
    "SimulationResponse",
    "ComparisonResponse",
    # alerts
    "InventoryAlert",
    "AlertsResponse",
    # chat
    "ChatMessage",
    "ToolCallRecord",
    "ChatRequest",
    "ChatResponse",
]
