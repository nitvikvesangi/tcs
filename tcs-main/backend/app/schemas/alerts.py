"""
Alerts Pydantic schemas.

Used by GET /api/v1/inventory/alerts (Phase 2).
Declared here in Phase 1 so the contract is stable.
"""

import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.utils.enums import InventoryAlertType, UrgencyLevel


class InventoryAlert(BaseModel):
    """
    A single machine-readable inventory alert.

    The `details` dict carries alert-type-specific fields:
      - OVERSTOCK: {"overstock_pct": 80, "days_of_supply": 45}
      - EXPIRY: {"days_until_expiry": 2, "batch_quantity": 50}
      - STOCKOUT: {"days_until_stockout": 1, "predicted_demand": 12}
      - etc.
    """
    store_id: int
    store_code: str
    product_id: int
    product_sku: str
    product_name: str
    alert_type: InventoryAlertType
    urgency: UrgencyLevel
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class AlertsResponse(BaseModel):
    """Response for GET /api/v1/inventory/alerts."""
    store_id: Optional[int] = Field(
        default=None,
        description="If provided, alerts are scoped to this store only",
    )
    total_alerts: int
    critical_count: int
    high_count: int
    alerts: List[InventoryAlert]
    generated_at: datetime.datetime
