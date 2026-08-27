"""
Inventory Service — Phase 2.

Calculates effective stock, detects alert conditions, and provides
store-level inventory views. All business logic lives here; routes are thin.

Alert thresholds (tunable):
  OVERSTOCK  : quantity_available > max_stock * 1.2  OR  > reorder_point * 5
  UNDERSTOCK : effective_stock < reorder_point
  STOCKOUT   : effective_stock == 0
  EXPIRY     : expiry_date <= today + 7 days
    0 days  → CRITICAL
    1-2     → URGENT (HIGH)
    3-7     → WARNING (MEDIUM)
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.context import Trend
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.store import DarkStore
from app.utils.enums import DemandTrend, InventoryAlertType, UrgencyLevel


# ---------------------------------------------------------------------------
# Core calculations (pure functions — no DB access)
# ---------------------------------------------------------------------------

def calc_effective_stock(quantity_available: int, quantity_reserved: int) -> int:
    return max(0, quantity_available - quantity_reserved)


def calc_days_until_expiry(expiry_date: Optional[datetime.date]) -> Optional[int]:
    if expiry_date is None:
        return None
    today = datetime.date.today()
    return (expiry_date - today).days


def classify_expiry_urgency(days: Optional[int]) -> UrgencyLevel:
    if days is None:
        return UrgencyLevel.LOW
    if days <= 0:
        return UrgencyLevel.CRITICAL
    if days <= 2:
        return UrgencyLevel.HIGH
    if days <= 7:
        return UrgencyLevel.MEDIUM
    return UrgencyLevel.LOW


def classify_stock_alerts(
    inv: Inventory,
    latest_trend: Optional[Trend] = None,
) -> List[Dict[str, Any]]:
    """
    Return a list of alert dicts for a single inventory record.
    Each dict has: alert_type, urgency, message, details.
    """
    alerts: List[Dict[str, Any]] = []
    effective = calc_effective_stock(inv.quantity_available, inv.quantity_reserved)
    days_left = calc_days_until_expiry(inv.expiry_date)

    # ---- STOCKOUT -----------------------------------------------------------
    if effective == 0 and inv.quantity_available >= 0:
        alerts.append({
            "alert_type": InventoryAlertType.STOCKOUT,
            "urgency": UrgencyLevel.CRITICAL,
            "message": "Product is completely out of stock",
            "details": {
                "quantity_available": inv.quantity_available,
                "quantity_reserved": inv.quantity_reserved,
                "effective_stock": 0,
            },
        })

    # ---- UNDERSTOCK ---------------------------------------------------------
    elif effective < inv.reorder_point:
        pct = round(effective / max(inv.reorder_point, 1) * 100, 1)
        urgency = UrgencyLevel.HIGH if pct < 25 else UrgencyLevel.MEDIUM
        alerts.append({
            "alert_type": InventoryAlertType.UNDERSTOCK,
            "urgency": urgency,
            "message": f"Stock is {100 - pct:.0f}% below reorder point",
            "details": {
                "effective_stock": effective,
                "reorder_point": inv.reorder_point,
                "stock_pct_of_reorder": pct,
            },
        })

    # ---- OVERSTOCK ----------------------------------------------------------
    if inv.max_stock and inv.quantity_available > inv.max_stock * 1.1:
        excess_pct = round((inv.quantity_available - inv.max_stock) / inv.max_stock * 100, 1)
        urgency = UrgencyLevel.CRITICAL if excess_pct > 50 else UrgencyLevel.HIGH
        alerts.append({
            "alert_type": InventoryAlertType.OVERSTOCK,
            "urgency": urgency,
            "message": f"Stock is {excess_pct:.0f}% above max capacity",
            "details": {
                "quantity_available": inv.quantity_available,
                "max_stock": inv.max_stock,
                "excess_pct": excess_pct,
            },
        })
    elif not inv.max_stock and inv.reorder_point > 0 and inv.quantity_available > inv.reorder_point * 5:
        alerts.append({
            "alert_type": InventoryAlertType.OVERSTOCK,
            "urgency": UrgencyLevel.MEDIUM,
            "message": f"Stock is {inv.quantity_available // max(inv.reorder_point,1)}x above reorder point",
            "details": {
                "quantity_available": inv.quantity_available,
                "reorder_point": inv.reorder_point,
            },
        })

    # ---- EXPIRY -------------------------------------------------------------
    if days_left is not None and days_left <= 7:
        urgency = classify_expiry_urgency(days_left)
        product_name = inv.product.name if inv.product else f"product {inv.product_id}"
        shelf_life = inv.product.shelf_life_days if inv.product else "?"
        alerts.append({
            "alert_type": InventoryAlertType.EXPIRY,
            "urgency": urgency,
            "message": (
                f"expiry_urgency={urgency.value.title()} "
                f"({max(0, days_left)} days left of {shelf_life}-day shelf life)"
            ),
            "details": {
                "expiry_date": inv.expiry_date.isoformat() if inv.expiry_date else None,
                "days_until_expiry": days_left,
                "batch_quantity": inv.quantity_available,
            },
        })

    # ---- DECLINING DEMAND ---------------------------------------------------
    if latest_trend and latest_trend.demand_trend == DemandTrend.DECLINING:
        alerts.append({
            "alert_type": InventoryAlertType.DECLINING_DEMAND,
            "urgency": UrgencyLevel.MEDIUM,
            "message": "Product demand is declining — consider promotion",
            "details": {
                "trend_score": float(latest_trend.trend_score),
                "demand_trend": latest_trend.demand_trend.value,
                "sales_velocity": float(latest_trend.sales_velocity) if latest_trend.sales_velocity else None,
            },
        })

    return alerts


# ---------------------------------------------------------------------------
# Composite urgency score (0–100) for inventory snapshot
# ---------------------------------------------------------------------------

def calc_inventory_alert_score(inv: Inventory, latest_trend: Optional[Trend] = None) -> Tuple[int, str, str, str]:
    """Returns (score, stockout_urgency, overstock_urgency, expiry_urgency) display strings."""
    effective = calc_effective_stock(inv.quantity_available, inv.quantity_reserved)
    days_left = calc_days_until_expiry(inv.expiry_date)
    score = 0

    # Stockout urgency
    if effective == 0:
        stockout_u = "Critical"
        score = max(score, 100)
    elif inv.reorder_point > 0 and effective < inv.reorder_point:
        pct = effective / inv.reorder_point
        stockout_u = "High" if pct < 0.25 else "Medium"
        score = max(score, 75 if pct < 0.25 else 50)
    else:
        stockout_u = "Low"

    # Overstock urgency
    if inv.max_stock and inv.quantity_available > inv.max_stock * 1.5:
        overstock_u = "Critical"
        score = max(score, 100)
    elif inv.max_stock and inv.quantity_available > inv.max_stock * 1.1:
        overstock_u = "High"
        score = max(score, 75)
    elif not inv.max_stock and inv.reorder_point > 0 and inv.quantity_available > inv.reorder_point * 5:
        overstock_u = "Medium"
        score = max(score, 50)
    else:
        overstock_u = "Low"

    # Expiry urgency
    exp_u_enum = classify_expiry_urgency(days_left)
    expiry_u = exp_u_enum.value.title()
    if exp_u_enum == UrgencyLevel.CRITICAL:
        score = max(score, 100)
    elif exp_u_enum == UrgencyLevel.HIGH:
        score = max(score, 80)
    elif exp_u_enum == UrgencyLevel.MEDIUM:
        score = max(score, 50)

    return score, stockout_u, overstock_u, expiry_u


# ---------------------------------------------------------------------------
# Database queries
# ---------------------------------------------------------------------------

class InventoryService:

    @staticmethod
    def get_store_inventory(
        db: Session,
        store_id: int,
        retailer_id: Optional[int] = None,
    ) -> List[Inventory]:
        """All inventory records for a store, with product eagerly loaded."""
        q = (
            db.query(Inventory)
            .options(joinedload(Inventory.product), joinedload(Inventory.dark_store))
            .filter(Inventory.dark_store_id == store_id)
        )
        if retailer_id is not None:
            q = q.join(DarkStore).filter(DarkStore.retailer_id == retailer_id)
        return q.all()

    @staticmethod
    def get_all_inventory(
        db: Session,
        retailer_id: Optional[int] = None,
        store_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Inventory]:
        q = (
            db.query(Inventory)
            .options(joinedload(Inventory.product), joinedload(Inventory.dark_store))
            .join(DarkStore)
        )
        if retailer_id is not None:
            q = q.filter(DarkStore.retailer_id == retailer_id)
        if store_id is not None:
            q = q.filter(Inventory.dark_store_id == store_id)
        return q.offset(skip).limit(limit).all()

    @staticmethod
    def get_inventory_by_id(db: Session, inventory_id: int) -> Optional[Inventory]:
        return (
            db.query(Inventory)
            .options(joinedload(Inventory.product), joinedload(Inventory.dark_store))
            .filter(Inventory.id == inventory_id)
            .first()
        )

    @staticmethod
    def update_inventory(db: Session, inv: Inventory, updates: Dict[str, Any]) -> Inventory:
        for field, value in updates.items():
            if hasattr(inv, field) and value is not None:
                setattr(inv, field, value)
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def get_alerts(
        db: Session,
        retailer_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Compute and return all active inventory alerts."""
        q = (
            db.query(Inventory)
            .options(
                joinedload(Inventory.product),
                joinedload(Inventory.dark_store),
            )
            .join(DarkStore)
        )
        if retailer_id is not None:
            q = q.filter(DarkStore.retailer_id == retailer_id)
        if store_id is not None:
            q = q.filter(Inventory.dark_store_id == store_id)

        inventory_records = q.all()
        result = []

        # Fetch latest trends in bulk
        product_ids = list({inv.product_id for inv in inventory_records})
        latest_trends: Dict[int, Trend] = {}
        if product_ids:
            subq = (
                db.query(Trend.product_id, func.max(Trend.date).label("max_date"))
                .filter(Trend.product_id.in_(product_ids))
                .group_by(Trend.product_id)
                .subquery()
            )
            trends = (
                db.query(Trend)
                .join(subq, (Trend.product_id == subq.c.product_id) & (Trend.date == subq.c.max_date))
                .all()
            )
            latest_trends = {t.product_id: t for t in trends}

        for inv in inventory_records:
            trend = latest_trends.get(inv.product_id)
            inv_alerts = classify_stock_alerts(inv, trend)
            for a in inv_alerts:
                result.append({
                    "store_id": inv.dark_store_id,
                    "store_code": inv.dark_store.code if inv.dark_store else "",
                    "product_id": inv.product_id,
                    "product_sku": inv.product.sku if inv.product else "",
                    "product_name": inv.product.name if inv.product else "",
                    **a,
                    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                })

        # Sort: CRITICAL first, then HIGH, MEDIUM, LOW
        urgency_order = {UrgencyLevel.CRITICAL: 0, UrgencyLevel.HIGH: 1, UrgencyLevel.MEDIUM: 2, UrgencyLevel.LOW: 3}
        result.sort(key=lambda x: urgency_order.get(x["urgency"], 99))
        return result
