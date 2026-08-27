"""
Analytics Service — Phase 3 (SQL-based, no ML).
All analytics are computed directly from the database via SQLAlchemy.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.context import Trend
from app.models.customer import Customer, CustomerEvent
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.promotion import Promotion
from app.models.store import DarkStore
from app.utils.enums import CustomerEventType, PromotionStatus


class AnalyticsService:

    # -----------------------------------------------------------------------
    # Sales analytics
    # -----------------------------------------------------------------------

    @staticmethod
    def sales_trend(
        db: Session,
        retailer_id: Optional[int],
        store_id: Optional[int],
        product_id: Optional[int],
        days: int = 30,
    ) -> Dict[str, Any]:
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        q = (
            db.query(
                func.date(Order.placed_at).label("date"),
                func.sum(OrderItem.quantity).label("units_sold"),
                func.sum(OrderItem.total_price).label("revenue"),
                func.sum(
                    OrderItem.quantity * (OrderItem.unit_price - func.coalesce(
                        db.query(Product.cost_price)
                        .filter(Product.id == OrderItem.product_id)
                        .correlate(OrderItem)
                        .scalar_subquery(),
                        0
                    ))
                ).label("profit"),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .join(DarkStore, DarkStore.id == Order.dark_store_id)
        )
        if retailer_id:
            q = q.filter(DarkStore.retailer_id == retailer_id)
        if store_id:
            q = q.filter(Order.dark_store_id == store_id)
        if product_id:
            q = q.filter(OrderItem.product_id == product_id)
        q = q.filter(func.date(Order.placed_at) >= cutoff).group_by(func.date(Order.placed_at)).order_by(func.date(Order.placed_at))
        rows = q.all()
        return {
            "store_id": store_id,
            "product_id": product_id,
            "period_days": days,
            "data_points": [
                {
                    "date": str(r.date),
                    "units_sold": int(r.units_sold or 0),
                    "revenue": float(r.revenue or 0),
                    "profit": float(r.profit or 0),
                }
                for r in rows
            ],
        }

    # -----------------------------------------------------------------------
    # Top products
    # -----------------------------------------------------------------------

    @staticmethod
    def top_products(
        db: Session,
        retailer_id: Optional[int],
        store_id: Optional[int],
        days: int = 30,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        q = (
            db.query(
                Product.id,
                Product.sku,
                Product.name,
                Product.category,
                func.sum(OrderItem.quantity).label("units_sold"),
                func.sum(OrderItem.total_price).label("revenue"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .join(DarkStore, DarkStore.id == Order.dark_store_id)
        )
        if retailer_id:
            q = q.filter(DarkStore.retailer_id == retailer_id)
        if store_id:
            q = q.filter(Order.dark_store_id == store_id)
        q = (
            q.filter(func.date(Order.placed_at) >= cutoff)
            .group_by(Product.id, Product.sku, Product.name, Product.category)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        return [
            {
                "product_id": r.id,
                "sku": r.sku,
                "name": r.name,
                "category": r.category,
                "units_sold": int(r.units_sold or 0),
                "revenue": float(r.revenue or 0),
            }
            for r in q.all()
        ]

    # -----------------------------------------------------------------------
    # Demand / trends
    # -----------------------------------------------------------------------

    @staticmethod
    def product_trends(
        db: Session,
        retailer_id: Optional[int],
        store_id: Optional[int],
        days: int = 7,
        limit: int = 20,
    ) -> Dict[str, Any]:
        today = datetime.date.today()
        cutoff = today - datetime.timedelta(days=days)
        q = (
            db.query(Trend)
            .join(Product, Product.id == Trend.product_id)
            .filter(Trend.date >= cutoff)
            .order_by(Trend.trend_score.desc())
            .limit(limit)
        )
        rows = q.all()
        return {
            "store_id": store_id,
            "date": str(today),
            "trending_products": [
                {
                    "product_id": t.product_id,
                    "product_sku": t.product.sku if t.product else "",
                    "product_name": t.product.name if t.product else "",
                    "trend_score": float(t.trend_score),
                    "demand_trend": t.demand_trend.value,
                    "sales_velocity": float(t.sales_velocity) if t.sales_velocity else None,
                }
                for t in rows
            ],
        }

    # -----------------------------------------------------------------------
    # Customer analytics
    # -----------------------------------------------------------------------

    @staticmethod
    def customer_analytics(
        db: Session,
        retailer_id: Optional[int],
        store_id: Optional[int],
        days: int = 30,
    ) -> Dict[str, Any]:
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
        q = (
            db.query(CustomerEvent.event_type, func.count(CustomerEvent.id))
            .join(DarkStore, DarkStore.id == CustomerEvent.dark_store_id)
        )
        if retailer_id:
            q = q.filter(DarkStore.retailer_id == retailer_id)
        if store_id:
            q = q.filter(CustomerEvent.dark_store_id == store_id)
        q = q.filter(CustomerEvent.created_at >= cutoff).group_by(CustomerEvent.event_type)
        counts = {r[0].value: r[1] for r in q.all()}

        views = counts.get(CustomerEventType.VIEW.value, 0)
        searches = counts.get(CustomerEventType.SEARCH.value, 0)
        cart_adds = counts.get(CustomerEventType.CART_ADD.value, 0)
        purchases = counts.get(CustomerEventType.PURCHASE.value, 0)

        # Repeat purchase rate
        repeat_q = (
            db.query(
                CustomerEvent.customer_id,
                func.count(CustomerEvent.id).label("cnt"),
            )
            .filter(
                CustomerEvent.event_type == CustomerEventType.PURCHASE,
                CustomerEvent.created_at >= cutoff,
            )
        )
        if store_id:
            repeat_q = repeat_q.filter(CustomerEvent.dark_store_id == store_id)
        repeat_rows = repeat_q.group_by(CustomerEvent.customer_id).all()
        total_buyers = len(repeat_rows)
        repeat_buyers = sum(1 for r in repeat_rows if r.cnt > 1)
        repeat_rate = round(repeat_buyers / max(total_buyers, 1) * 100, 1)

        return {
            "store_id": store_id,
            "period_days": days,
            "total_views": views,
            "total_searches": searches,
            "total_cart_adds": cart_adds,
            "total_purchases": purchases,
            "view_to_purchase_rate": round(purchases / max(views, 1) * 100, 2),
            "cart_to_purchase_rate": round(purchases / max(cart_adds, 1) * 100, 2),
            "repeat_purchase_rate": repeat_rate,
        }

    # -----------------------------------------------------------------------
    # Store comparison
    # -----------------------------------------------------------------------

    @staticmethod
    def store_comparison(
        db: Session,
        retailer_id: Optional[int],
        days: int = 30,
    ) -> Dict[str, Any]:
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        stores = db.query(DarkStore)
        if retailer_id:
            stores = stores.filter(DarkStore.retailer_id == retailer_id)
        stores = stores.all()

        result = []
        for store in stores:
            # Revenue
            rev_row = (
                db.query(func.sum(OrderItem.total_price))
                .join(Order, Order.id == OrderItem.order_id)
                .filter(Order.dark_store_id == store.id)
                .filter(func.date(Order.placed_at) >= cutoff)
                .scalar()
            )
            # Units
            units_row = (
                db.query(func.sum(OrderItem.quantity))
                .join(Order, Order.id == OrderItem.order_id)
                .filter(Order.dark_store_id == store.id)
                .filter(func.date(Order.placed_at) >= cutoff)
                .scalar()
            )
            # Active promotions
            promo_count = (
                db.query(func.count(Promotion.id))
                .filter(Promotion.dark_store_id == store.id, Promotion.status == PromotionStatus.APPROVED)
                .scalar()
            )
            # Inventory alerts (simplified count)
            from app.services.inventory import InventoryService
            alerts = InventoryService.get_alerts(db, store_id=store.id)
            result.append({
                "store_id": store.id,
                "store_code": store.code,
                "store_city": store.city,
                "total_revenue": float(rev_row or 0),
                "total_profit": 0.0,  # would need cost join
                "units_sold": int(units_row or 0),
                "active_promotions": int(promo_count or 0),
                "inventory_alert_count": len(alerts),
            })

        return {"period_days": days, "stores": result}

    # -----------------------------------------------------------------------
    # Demand forecast (simple moving average)
    # -----------------------------------------------------------------------

    @staticmethod
    def demand_forecast(
        db: Session,
        product_id: int,
        store_id: int,
        forecast_days: int = 7,
    ) -> Dict[str, Any]:
        # Compute 14-day average daily demand
        cutoff = datetime.date.today() - datetime.timedelta(days=14)
        total = (
            db.query(func.sum(OrderItem.quantity))
            .join(Order, Order.id == OrderItem.order_id)
            .filter(
                OrderItem.product_id == product_id,
                Order.dark_store_id == store_id,
                func.date(Order.placed_at) >= cutoff,
            )
            .scalar()
        )
        avg_daily = float(total or 0) / 14

        # Trend adjustment
        trend = (
            db.query(Trend)
            .filter(Trend.product_id == product_id)
            .order_by(Trend.date.desc())
            .first()
        )
        trend_factor = 1.0
        if trend:
            if trend.demand_trend.value == "INCREASING":
                trend_factor = 1.1
            elif trend.demand_trend.value == "DECLINING":
                trend_factor = 0.9

        adjusted = avg_daily * trend_factor
        variance = adjusted * 0.2  # ±20% bounds

        forecast = []
        for i in range(1, forecast_days + 1):
            d = datetime.date.today() + datetime.timedelta(days=i)
            forecast.append({
                "date": str(d),
                "predicted_units": round(adjusted, 1),
                "lower_bound": round(max(0, adjusted - variance), 1),
                "upper_bound": round(adjusted + variance, 1),
            })

        return {
            "product_id": product_id,
            "store_id": store_id,
            "forecast_days": forecast_days,
            "forecast": forecast,
        }
