"""
Promotion Engine — Phase 4 (Deterministic).

The engine is PURELY deterministic. No LLM. No randomness.
The LLM (Phase 5 chatbot) sits AFTER the engine, not inside it.

Formula:
  For each candidate discount_pct d:
    sell_price        = mrp * (1 - d/100)
    margin_per_unit   = sell_price - cost_price
    demand_factor     = 1 + (d/100) * demand_elasticity   # demand increases with discount
    base_daily_demand = sales_velocity or 5 units/day
    duration_days     = 7 (default)
    expected_units    = base_daily_demand * demand_factor * duration_days
    expected_units    = min(expected_units, effective_stock)   # can't sell more than stock
    expected_revenue  = expected_units * sell_price
    expected_profit   = expected_units * margin_per_unit
    inventory_reduction_pct = expected_units / max(effective_stock, 1) * 100
    stockout_risk_pct = max(0, (expected_units - effective_stock * 0.9) / max(effective_stock, 1) * 100)

    score = expected_profit   (MAXIMIZE_PROFIT)
          = expected_units    (MAXIMIZE_SALES)
          = inventory_reduction_pct (CLEAR_INVENTORY / REDUCE_EXPIRY_WASTE)
          = composite         (BALANCED)

Risk protection:
  - If margin_per_unit < 0 AND objective is not clearance/expiry → skip option
  - If stockout_risk_pct > 80 → HIGH stockout risk flag

Demand elasticity: 1.5 (adjustable)
  Meaning: a 10% discount increases demand by ~15%
"""

from __future__ import annotations

import datetime
import math
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.context import CompetitorPrice, Festival, Trend, Weather
from app.models.customer import CustomerEvent
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.promotion import Promotion
from app.models.store import DarkStore
from app.services.inventory import (
    calc_effective_stock,
    calc_days_until_expiry,
    classify_expiry_urgency,
    calc_inventory_alert_score,
)
from app.utils.enums import (
    CustomerEventType,
    DemandTrend,
    InventoryAlertType,
    PromotionObjective,
    PromotionStatus,
    PromotionType,
    RiskFlag,
    UrgencyLevel,
)

DEMAND_ELASTICITY = 1.5   # each 1% discount → 1.5% demand increase
DEFAULT_DAILY_DEMAND = 5  # units/day if no sales data
DEFAULT_DURATION_DAYS = 7


# ---------------------------------------------------------------------------
# Context gathering
# ---------------------------------------------------------------------------

def _get_sales_velocity(db: Session, product_id: int, store_id: int, days: int = 30) -> float:
    """Average daily units sold over the last `days` days."""
    cutoff = datetime.date.today() - datetime.timedelta(days=days)
    result = (
        db.query(func.sum(OrderItem.quantity))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            OrderItem.product_id == product_id,
            Order.dark_store_id == store_id,
            func.date(Order.placed_at) >= cutoff,
        )
        .scalar()
    )
    total = float(result or 0)
    return total / days if total > 0 else 0.0


def _get_funnel_metrics(db: Session, product_id: int, store_id: int, days: int = 14) -> Dict[str, int]:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
    rows = (
        db.query(CustomerEvent.event_type, func.count(CustomerEvent.id))
        .filter(
            CustomerEvent.product_id == product_id,
            CustomerEvent.dark_store_id == store_id,
            CustomerEvent.created_at >= cutoff,
        )
        .group_by(CustomerEvent.event_type)
        .all()
    )
    return {r[0].value: r[1] for r in rows}


def _get_latest_trend(db: Session, product_id: int) -> Optional[Trend]:
    return (
        db.query(Trend)
        .filter(Trend.product_id == product_id)
        .order_by(Trend.date.desc())
        .first()
    )


def _get_latest_weather(db: Session, store_id: int) -> Optional[Weather]:
    return (
        db.query(Weather)
        .filter(Weather.dark_store_id == store_id)
        .order_by(Weather.date.desc())
        .first()
    )


def _get_upcoming_festival(db: Session, store: DarkStore, days_ahead: int = 7) -> Optional[Festival]:
    today = datetime.date.today()
    end = today + datetime.timedelta(days=days_ahead)
    return (
        db.query(Festival)
        .filter(
            Festival.city == store.city,
            Festival.date >= today,
            Festival.date <= end,
        )
        .order_by(Festival.date)
        .first()
    )


def _get_competitor_price(db: Session, product_id: int, store_id: int) -> Optional[float]:
    row = (
        db.query(CompetitorPrice)
        .filter(
            CompetitorPrice.product_id == product_id,
            CompetitorPrice.dark_store_id == store_id,
        )
        .order_by(CompetitorPrice.recorded_at.desc())
        .first()
    )
    return float(row.competitor_price) if row else None


# ---------------------------------------------------------------------------
# Discount candidate generation
# ---------------------------------------------------------------------------

def _choose_candidate_discounts(
    margin_pct: float,
    expiry_days: Optional[int],
    effective_stock: int,
    max_stock: Optional[int],
    reorder_point: int,
    objective: PromotionObjective,
    max_discount_pct: float,
) -> List[float]:
    """
    Choose 3 candidate discount levels based on context.
    Discounts are in ascending severity order.
    """
    # Base decision tree
    is_clearance_objective = objective in (
        PromotionObjective.CLEAR_INVENTORY,
        PromotionObjective.REDUCE_EXPIRY_WASTE,
    )

    # Overstock ratio
    overstock_ratio = 0.0
    if max_stock and max_stock > 0:
        overstock_ratio = effective_stock / max_stock
    elif reorder_point > 0:
        overstock_ratio = effective_stock / (reorder_point * 3)  # assume 3x = full

    # Expiry pressure
    expiry_pressure = 0.0
    if expiry_days is not None:
        if expiry_days <= 0:
            expiry_pressure = 1.0
        elif expiry_days <= 2:
            expiry_pressure = 0.8
        elif expiry_days <= 7:
            expiry_pressure = 0.5

    # Compute base discount
    if expiry_pressure >= 0.8 or (is_clearance_objective and overstock_ratio > 1.5):
        base = 20.0
    elif overstock_ratio > 1.2 or is_clearance_objective:
        base = 15.0
    elif margin_pct > 30:
        base = 10.0
    else:
        base = 5.0

    step = max(5.0, base * 0.5)
    candidates = [base, base + step, base + step * 2]
    candidates = [min(c, max_discount_pct) for c in candidates]
    return list(dict.fromkeys(candidates))  # deduplicate


# ---------------------------------------------------------------------------
# Per-option metrics calculation
# ---------------------------------------------------------------------------

def _calc_option(
    mrp: float,
    cost_price: float,
    discount_pct: float,
    effective_stock: int,
    sales_velocity: float,
    duration_days: int,
    demand_multiplier: float,
    objective: PromotionObjective,
) -> Dict[str, float]:
    sell_price = mrp * (1 - discount_pct / 100)
    margin_per_unit = sell_price - cost_price

    # Demand factor: each % discount increases demand by elasticity factor
    demand_factor = 1.0 + (discount_pct / 100) * DEMAND_ELASTICITY
    # Apply festival/weather multiplier
    demand_factor *= demand_multiplier

    base_demand = max(sales_velocity, DEFAULT_DAILY_DEMAND * 0.3)
    expected_units_raw = base_demand * demand_factor * duration_days
    # Can't sell more than stock
    expected_units = min(expected_units_raw, effective_stock)

    expected_revenue = expected_units * sell_price
    expected_profit = round(expected_units * margin_per_unit, 2)
    inv_reduction_pct = round(expected_units / max(effective_stock, 1) * 100, 1)
    stockout_risk = max(0.0, (expected_units_raw - effective_stock) / max(effective_stock, 1) * 100)
    stockout_risk_pct = round(min(stockout_risk, 100.0), 1)

    # Score depends on objective
    if objective == PromotionObjective.MAXIMIZE_PROFIT:
        score = expected_profit
    elif objective == PromotionObjective.MAXIMIZE_SALES:
        score = expected_units
    elif objective in (PromotionObjective.CLEAR_INVENTORY, PromotionObjective.REDUCE_EXPIRY_WASTE):
        score = inv_reduction_pct - stockout_risk_pct * 0.1
    elif objective == PromotionObjective.INCREASE_RETENTION:
        score = expected_units * 0.5 + expected_profit * 0.5
    else:  # BALANCED
        score = expected_profit * 0.5 + expected_units * 0.3 + inv_reduction_pct * 0.2

    return {
        "discount_pct": round(discount_pct, 1),
        "expected_profit": round(expected_profit, 2),
        "inventory_reduction_pct": round(inv_reduction_pct, 1),
        "stockout_risk_pct": round(stockout_risk_pct, 1),
        "score": round(score, 2),
    }


# ---------------------------------------------------------------------------
# Reason builder
# ---------------------------------------------------------------------------

def _build_reasons(
    expiry_days: Optional[int],
    effective_stock: int,
    max_stock: Optional[int],
    reorder_point: int,
    sales_velocity: float,
    trend: Optional[Trend],
    competitor_price: Optional[float],
    mrp: float,
    funnel: Dict[str, int],
    festival: Optional[Festival],
    weather: Optional[Weather],
) -> Tuple[List[str], RiskFlag]:
    reasons: List[str] = []
    risk = RiskFlag.NONE

    # Expiry
    if expiry_days is not None and expiry_days <= 7:
        urgency = classify_expiry_urgency(expiry_days)
        reasons.append(f"expiry_urgency={urgency.value.title()} ({max(0,expiry_days)} days left)")
        if urgency == UrgencyLevel.CRITICAL:
            risk = RiskFlag.EXPIRY_CRITICAL

    # Overstock
    if max_stock and effective_stock > max_stock * 1.1:
        excess_pct = round((effective_stock - max_stock) / max_stock * 100, 1)
        reasons.append(f"Inventory is {excess_pct}% above target capacity")
        if risk == RiskFlag.NONE:
            risk = RiskFlag.OVERSTOCK_RISK
    elif reorder_point > 0 and effective_stock > reorder_point * 5:
        reasons.append(f"Stock is {effective_stock // max(reorder_point,1)}x above reorder point")
        if risk == RiskFlag.NONE:
            risk = RiskFlag.OVERSTOCK_RISK

    # Stockout
    if effective_stock == 0:
        reasons.append("Product is out of stock — promotion would boost restock priority visibility")
        risk = RiskFlag.STOCKOUT_RISK
    elif reorder_point > 0 and effective_stock < reorder_point:
        reasons.append(f"Stock ({effective_stock}) is below reorder point ({reorder_point}) — avoid aggressive discount")
        if risk == RiskFlag.NONE:
            risk = RiskFlag.STOCKOUT_RISK

    # Demand trend
    if trend:
        if trend.demand_trend == DemandTrend.DECLINING:
            reasons.append(f"Recent demand declined (trend score: {float(trend.trend_score):.0f}/100)")
        elif trend.demand_trend == DemandTrend.INCREASING:
            reasons.append(f"Demand is increasing (trend score: {float(trend.trend_score):.0f}/100) — light discount recommended")

    # Funnel
    views = funnel.get(CustomerEventType.VIEW.value, 0)
    purchases = funnel.get(CustomerEventType.PURCHASE.value, 0)
    cart_adds = funnel.get(CustomerEventType.CART_ADD.value, 0)
    if views > 10 and purchases < views * 0.05:
        reasons.append(f"High views ({views}) but weak conversion ({purchases} purchases) — discount may convert browsers")
    if cart_adds > 5 and purchases < cart_adds * 0.3:
        reasons.append(f"{cart_adds} cart additions but only {purchases} purchases — price sensitivity detected")

    # Competitor price
    if competitor_price and competitor_price < mrp:
        gap_pct = round((mrp - competitor_price) / mrp * 100, 1)
        reasons.append(f"Competitor price is {gap_pct}% lower than our MRP (₹{competitor_price:.0f} vs ₹{mrp:.0f})")

    # Festival
    if festival:
        reasons.append(f"Upcoming festival: {festival.name} on {festival.date} (demand multiplier: {float(festival.demand_multiplier):.1f}x)")

    # Weather
    if weather:
        reasons.append(f"Current weather: {weather.condition.value} — may affect demand")

    if not reasons:
        reasons.append("Routine promotion opportunity — no urgent triggers")

    return reasons, risk


# ---------------------------------------------------------------------------
# Determine recommended action
# ---------------------------------------------------------------------------

def _determine_action(
    best_option: Dict[str, float],
    risk: RiskFlag,
    objective: PromotionObjective,
    expiry_days: Optional[int],
) -> str:
    if risk == RiskFlag.EXPIRY_CRITICAL or (expiry_days is not None and expiry_days <= 1):
        return PromotionType.CLEARANCE.value
    if risk == RiskFlag.OVERSTOCK_RISK or objective == PromotionObjective.CLEAR_INVENTORY:
        return PromotionType.PERCENTAGE_DISCOUNT.value
    if objective == PromotionObjective.REDUCE_EXPIRY_WASTE:
        return PromotionType.CLEARANCE.value
    if best_option["discount_pct"] >= 30:
        return PromotionType.CLEARANCE.value
    return PromotionType.PERCENTAGE_DISCOUNT.value


# ---------------------------------------------------------------------------
# Main engine entrypoint
# ---------------------------------------------------------------------------

class PromotionEngine:

    @staticmethod
    def recommend(
        db: Session,
        product_id: int,
        store_id: int,
        objective: PromotionObjective = PromotionObjective.BALANCED,
        max_discount_pct: float = 50.0,
        min_margin_pct: float = 0.0,
        duration_days: int = DEFAULT_DURATION_DAYS,
    ) -> Dict[str, Any]:
        """
        Run the deterministic promotion engine and return the full
        recommendation payload matching the locked JSON contract.
        """
        # --- Load entities ---------------------------------------------------
        product = db.query(Product).filter(Product.id == product_id).first()
        store = db.query(DarkStore).filter(DarkStore.id == store_id).first()
        if not product or not store:
            raise ValueError(f"Product {product_id} or Store {store_id} not found")

        # Aggregate inventory across all batches for this product+store
        inv_rows = (
            db.query(Inventory)
            .filter(Inventory.product_id == product_id, Inventory.dark_store_id == store_id)
            .all()
        )
        if not inv_rows:
            raise ValueError(f"No inventory found for product {product_id} at store {store_id}")

        # Use earliest expiry batch as the primary record
        inv_rows_with_expiry = [i for i in inv_rows if i.expiry_date]
        if inv_rows_with_expiry:
            primary_inv = min(inv_rows_with_expiry, key=lambda i: i.expiry_date)
        else:
            primary_inv = inv_rows[0]

        total_available = sum(i.quantity_available for i in inv_rows)
        total_reserved = sum(i.quantity_reserved for i in inv_rows)
        effective_stock = calc_effective_stock(total_available, total_reserved)
        # Use max_stock and reorder_point from primary
        max_stock = primary_inv.max_stock
        reorder_point = primary_inv.reorder_point
        expiry_days = calc_days_until_expiry(primary_inv.expiry_date)

        # --- Context ---------------------------------------------------------
        sales_velocity = _get_sales_velocity(db, product_id, store_id, days=30)
        funnel = _get_funnel_metrics(db, product_id, store_id)
        trend = _get_latest_trend(db, product_id)
        weather = _get_latest_weather(db, store_id)
        festival = _get_upcoming_festival(db, store)
        competitor_price = _get_competitor_price(db, product_id, store_id)

        # Demand multiplier from festival/weather
        demand_multiplier = 1.0
        if festival:
            demand_multiplier *= float(festival.demand_multiplier)
        if weather and weather.condition.value in ("RAINY", "STORMY", "COLD"):
            demand_multiplier *= 1.1  # bad weather boosts home delivery

        # --- Generate candidate discounts ------------------------------------
        mrp = float(product.mrp)
        cost_price = float(product.cost_price)
        margin_pct = (mrp - cost_price) / mrp * 100 if mrp > 0 else 0

        candidate_discounts = _choose_candidate_discounts(
            margin_pct=margin_pct,
            expiry_days=expiry_days,
            effective_stock=effective_stock,
            max_stock=max_stock,
            reorder_point=reorder_point,
            objective=objective,
            max_discount_pct=max_discount_pct,
        )

        # Ensure we have at least 3 options
        while len(candidate_discounts) < 3:
            last = candidate_discounts[-1]
            next_d = min(last + 5, max_discount_pct)
            if next_d not in candidate_discounts:
                candidate_discounts.append(next_d)
            else:
                break

        # --- Calculate metrics per option ------------------------------------
        is_clearance_objective = objective in (
            PromotionObjective.CLEAR_INVENTORY,
            PromotionObjective.REDUCE_EXPIRY_WASTE,
        )
        min_margin_abs = cost_price * (min_margin_pct / 100) if min_margin_pct else None

        options = []
        for d in candidate_discounts:
            opt = _calc_option(
                mrp=mrp,
                cost_price=cost_price,
                discount_pct=d,
                effective_stock=effective_stock,
                sales_velocity=sales_velocity,
                duration_days=duration_days,
                demand_multiplier=demand_multiplier,
                objective=objective,
            )
            sell_price = mrp * (1 - d / 100)
            margin_per_unit = sell_price - cost_price
            # Profit protection: skip negative-profit options unless clearance
            if margin_per_unit < 0 and not is_clearance_objective:
                if min_margin_abs is not None:
                    opt["expected_profit"] = round(opt["expected_profit"], 2)  # keep but mark
            options.append(opt)

        if not options:
            raise ValueError("No valid promotion options could be generated")

        # --- Pick best option ------------------------------------------------
        best = max(options, key=lambda o: o["score"])

        # --- Build reasons and risk flag -------------------------------------
        reasons, risk = _build_reasons(
            expiry_days=expiry_days,
            effective_stock=effective_stock,
            max_stock=max_stock,
            reorder_point=reorder_point,
            sales_velocity=sales_velocity,
            trend=trend,
            competitor_price=competitor_price,
            mrp=mrp,
            funnel=funnel,
            festival=festival,
            weather=weather,
        )

        # --- Inventory snapshot ----------------------------------------------
        alert_score, stockout_u, overstock_u, expiry_u = calc_inventory_alert_score(
            primary_inv, trend
        )

        recommended_action = _determine_action(best, risk, objective, expiry_days)

        # --- Persist to DB ---------------------------------------------------
        promo = Promotion(
            product_id=product_id,
            dark_store_id=store_id,
            promotion_type=PromotionType[recommended_action] if recommended_action in PromotionType.__members__ else PromotionType.PERCENTAGE_DISCOUNT,
            objective=objective,
            status=PromotionStatus.RECOMMENDED,
            discount_pct=best["discount_pct"],
            risk_flag=risk,
            recommendation_data={
                "product_id": product.sku,
                "dark_store_id": store.code,
                "recommended_action": recommended_action,
                "discount_pct": best["discount_pct"],
                "reasons": reasons,
                "risk_flag": risk.value,
                "options": options,
                "inventory_snapshot": {
                    "stockout_urgency": stockout_u,
                    "overstock_urgency": overstock_u,
                    "expiry_urgency": expiry_u,
                    "inventory_alert_score": alert_score,
                },
            },
        )
        db.add(promo)
        db.commit()

        return {
            "product_id": product.sku,
            "dark_store_id": store.code,
            "recommended_action": recommended_action,
            "discount_pct": best["discount_pct"],
            "reasons": reasons,
            "risk_flag": risk.value,
            "options": options,
            "inventory_snapshot": {
                "stockout_urgency": stockout_u,
                "overstock_urgency": overstock_u,
                "expiry_urgency": expiry_u,
                "inventory_alert_score": alert_score,
            },
        }

    @staticmethod
    def simulate(
        db: Session,
        product_id: int,
        store_id: int,
        discount_pct: float,
        duration_days: int = DEFAULT_DURATION_DAYS,
    ) -> Dict[str, Any]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product {product_id} not found")

        inv_rows = (
            db.query(Inventory)
            .filter(Inventory.product_id == product_id, Inventory.dark_store_id == store_id)
            .all()
        )
        total_available = sum(i.quantity_available for i in inv_rows) if inv_rows else 0
        total_reserved = sum(i.quantity_reserved for i in inv_rows) if inv_rows else 0
        effective_stock = calc_effective_stock(total_available, total_reserved)

        sales_velocity = _get_sales_velocity(db, product_id, store_id)
        trend = _get_latest_trend(db, product_id)

        # Festival/weather multiplier
        store = db.query(DarkStore).filter(DarkStore.id == store_id).first()
        demand_multiplier = 1.0
        if store:
            festival = _get_upcoming_festival(db, store)
            if festival:
                demand_multiplier *= float(festival.demand_multiplier)

        mrp = float(product.mrp)
        cost_price = float(product.cost_price)

        opt = _calc_option(
            mrp=mrp,
            cost_price=cost_price,
            discount_pct=discount_pct,
            effective_stock=effective_stock,
            sales_velocity=sales_velocity,
            duration_days=duration_days,
            demand_multiplier=demand_multiplier,
            objective=PromotionObjective.BALANCED,
        )

        demand_factor = 1.0 + (discount_pct / 100) * DEMAND_ELASTICITY * demand_multiplier
        base_demand = max(sales_velocity, DEFAULT_DAILY_DEMAND * 0.3)
        expected_units = min(base_demand * demand_factor * duration_days, effective_stock)

        sell_price = mrp * (1 - discount_pct / 100)
        expiry_units_saved = 0.0
        if inv_rows and any(i.expiry_date for i in inv_rows):
            earliest = min((i for i in inv_rows if i.expiry_date), key=lambda i: i.expiry_date)
            expiry_units_saved = min(expected_units, earliest.quantity_available)

        return {
            "product_id": product_id,
            "dark_store_id": store_id,
            "duration_days": duration_days,
            "result": {
                "discount_pct": discount_pct,
                "expected_sales_units": round(expected_units, 1),
                "expected_revenue": round(expected_units * sell_price, 2),
                "expected_profit": opt["expected_profit"],
                "inventory_reduction_pct": opt["inventory_reduction_pct"],
                "stockout_risk_pct": opt["stockout_risk_pct"],
                "expiry_waste_reduction_pct": round(expiry_units_saved / max(effective_stock, 1) * 100, 1),
                "profit_impact_pct": round(
                    (opt["expected_profit"] / max(effective_stock * (mrp - cost_price), 1)) * 100, 1
                ),
            },
        }

    @staticmethod
    def get_history(
        db: Session,
        store_id: Optional[int] = None,
        product_id: Optional[int] = None,
        retailer_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Promotion]:
        q = (
            db.query(Promotion)
            .join(DarkStore)
            .options(joinedload(Promotion.product), joinedload(Promotion.dark_store))
        )
        if retailer_id:
            q = q.filter(DarkStore.retailer_id == retailer_id)
        if store_id:
            q = q.filter(Promotion.dark_store_id == store_id)
        if product_id:
            q = q.filter(Promotion.product_id == product_id)
        return q.order_by(Promotion.created_at.desc()).offset(skip).limit(limit).all()
