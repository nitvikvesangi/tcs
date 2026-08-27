"""
Demo-mode chatbot service — Phase 5.

If GEMINI_API_KEY (or OPENAI_API_KEY) is configured, delegates to the LLM.
Otherwise runs in DEMO MODE: parses the user message for intent and calls
the appropriate backend service to return a real data-driven answer.

Demo mode tools:
  - inventory_alerts  → InventoryService.get_alerts
  - promotion_recommend → PromotionEngine.recommend
  - sales_trend       → AnalyticsService.sales_trend
  - store_list        → DB query

LLM integration is isolated behind ChatBackend protocol — swap implementations
without changing the route handler.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.store import DarkStore
from app.utils.enums import InventoryAlertType, PromotionObjective, UrgencyLevel


# ---------------------------------------------------------------------------
# Intent classifier (simple keyword matching for demo mode)
# ---------------------------------------------------------------------------

def _classify_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["overstock", "overstocked", "too much stock", "excess"]):
        return "overstock"
    if any(k in t for k in ["expir", "expire", "shelf life", "clearance"]):
        return "expiry"
    if any(k in t for k in ["stockout", "out of stock", "understock", "low stock", "reorder"]):
        return "stockout"
    if any(k in t for k in ["discount", "recommend", "promote", "promotion", "why should i discount"]):
        return "promotion_recommend"
    if any(k in t for k in ["simulate", "simulate", "what if", "what happen", "20%", "give % discount"]):
        return "simulate"
    if any(k in t for k in ["alert", "warning", "urgent"]):
        return "alerts"
    if any(k in t for k in ["sale", "revenue", "trend", "demand", "analytics"]):
        return "analytics"
    if any(k in t for k in ["store", "dark store", "location", "city"]):
        return "stores"
    return "general"


def _extract_product_sku(text: str) -> Optional[str]:
    """Extract product SKU like P0059 from text."""
    m = re.search(r'\b(P\d{4})\b', text.upper())
    return m.group(1) if m else None


def _extract_discount_pct(text: str) -> Optional[float]:
    m = re.search(r'(\d+)\s*%', text)
    return float(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Demo mode response builder
# ---------------------------------------------------------------------------

def _demo_response(db: Session, intent: str, message: str, store_id: Optional[int]) -> Dict[str, Any]:
    from app.services.inventory import InventoryService
    from app.services.analytics import AnalyticsService
    from app.services.promotion import PromotionEngine

    tool_calls = []
    response_text = ""

    if intent in ("overstock", "stockout", "expiry", "alerts"):
        alerts = InventoryService.get_alerts(db, store_id=store_id)
        tool_calls.append({"tool_name": "inventory_alerts", "arguments": {"store_id": store_id}, "result_summary": f"{len(alerts)} alerts found"})

        # Filter by intent
        if intent == "overstock":
            relevant = [a for a in alerts if a["alert_type"] == InventoryAlertType.OVERSTOCK]
            label = "overstocked products"
        elif intent == "expiry":
            relevant = [a for a in alerts if a["alert_type"] == InventoryAlertType.EXPIRY]
            label = "products with expiry alerts"
        elif intent == "stockout":
            relevant = [a for a in alerts if a["alert_type"] in (InventoryAlertType.STOCKOUT, InventoryAlertType.UNDERSTOCK)]
            label = "products at stockout/understock risk"
        else:
            relevant = alerts
            label = "active alerts"

        if not relevant:
            response_text = f"✅ No {label} found" + (" for the selected store." if store_id else ".")
        else:
            lines = [f"Found **{len(relevant)} {label}**:\n"]
            for a in relevant[:8]:
                urg_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(a["urgency"].value if hasattr(a["urgency"], "value") else str(a["urgency"]), "⚪")
                lines.append(f"{urg_emoji} **{a['product_name']}** ({a['product_sku']}) @ Store {a['store_code']}: {a['message']}")
            response_text = "\n".join(lines)

    elif intent == "promotion_recommend":
        sku = _extract_product_sku(message)
        product = None
        if sku:
            product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            # Pick first product with inventory
            inv = db.query(Inventory).first()
            if inv:
                product = db.query(Product).filter(Product.id == inv.product_id).first()

        if product:
            inv_rows = db.query(Inventory).filter(Inventory.product_id == product.id)
            if store_id:
                inv_rows = inv_rows.filter(Inventory.dark_store_id == store_id)
            inv = inv_rows.first()
            sid = store_id or (inv.dark_store_id if inv else None)
            if sid:
                try:
                    rec = PromotionEngine.recommend(db, product.id, sid, objective=PromotionObjective.BALANCED)
                    tool_calls.append({"tool_name": "promotion_recommend", "arguments": {"product_id": product.id, "store_id": sid}, "result_summary": f"Recommended {rec['discount_pct']}% discount"})
                    opts = rec["options"]
                    snap = rec["inventory_snapshot"]
                    lines = [
                        f"### Promotion Recommendation for **{product.name}** ({product.sku})",
                        f"**Recommended action:** {rec['recommended_action']} — **{rec['discount_pct']}% discount**",
                        f"**Risk:** {rec['risk_flag']}",
                        "",
                        "**Why:**",
                    ] + [f"- {r}" for r in rec["reasons"]] + [
                        "",
                        "**Options:**",
                    ] + [
                        f"- {o['discount_pct']}% off → profit ₹{o['expected_profit']:.1f}, stock reduction {o['inventory_reduction_pct']}%, score {o['score']:.1f}"
                        for o in opts
                    ] + [
                        "",
                        f"**Inventory:** Stockout={snap['stockout_urgency']}, Overstock={snap['overstock_urgency']}, Expiry={snap['expiry_urgency']}, Score={snap['inventory_alert_score']}/100",
                    ]
                    response_text = "\n".join(lines)
                except Exception as e:
                    response_text = f"Could not generate recommendation: {e}"
            else:
                response_text = "No store context available. Please specify a store."
        else:
            response_text = "Please specify a product SKU (e.g. P0001) to get a promotion recommendation."

    elif intent == "analytics":
        try:
            data = AnalyticsService.sales_trend(db, retailer_id=None, store_id=store_id, product_id=None, days=7)
            tool_calls.append({"tool_name": "sales_trend", "arguments": {"days": 7}, "result_summary": f"{len(data['data_points'])} days of data"})
            total_rev = sum(d["revenue"] for d in data["data_points"])
            total_units = sum(d["units_sold"] for d in data["data_points"])
            response_text = (
                f"📊 **Sales (last 7 days)**\n"
                f"- Total Revenue: ₹{total_rev:,.0f}\n"
                f"- Total Units Sold: {total_units:,}\n"
                f"- Data points: {len(data['data_points'])} days\n"
                "\nUse GET /api/v1/analytics/sales for the full dataset."
            )
        except Exception as e:
            response_text = f"Analytics error: {e}"

    elif intent == "stores":
        stores = db.query(DarkStore).limit(10).all()
        tool_calls.append({"tool_name": "store_list", "arguments": {}, "result_summary": f"{len(stores)} stores"})
        lines = ["**Active Dark Stores:**"]
        for s in stores:
            lines.append(f"- **{s.code}** — {s.name}, {s.city} ({s.status.value})")
        response_text = "\n".join(lines)

    else:
        response_text = (
            "I'm the Quick Commerce AI assistant in **demo mode**. I can help with:\n\n"
            "- 📦 `Which products are overstocked?`\n"
            "- ⏰ `Which products are expiring soon?`\n"
            "- 📉 `Which store has the highest stockout risk?`\n"
            "- 💡 `Why should I discount P0001?`\n"
            "- 📊 `Show me recent sales analytics`\n"
            "- 🏪 `List all stores`\n\n"
            "Configure `GEMINI_API_KEY` in `.env` to enable full AI responses."
        )

    return {
        "response": response_text,
        "tool_calls_made": tool_calls,
        "demo_mode": True,
    }


# ---------------------------------------------------------------------------
# LLM backend (stubbed — extend in Phase 5+)
# ---------------------------------------------------------------------------

def _llm_response(messages: List[Dict], store_id: Optional[int]) -> Dict[str, Any]:
    """Placeholder for real LLM integration (Gemini / OpenAI)."""
    return {
        "response": "LLM integration is configured but not yet implemented. Currently running in demo mode.",
        "tool_calls_made": [],
        "demo_mode": True,
    }


# ---------------------------------------------------------------------------
# Public chat function
# ---------------------------------------------------------------------------

def chat(
    db: Session,
    messages: List[Dict[str, str]],
    store_id: Optional[int] = None,
    product_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Main chat entrypoint.
    Checks for API key → routes to LLM or demo mode.
    """
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))

    if has_api_key:
        return _llm_response(messages, store_id)

    intent = _classify_intent(last_user)
    result = _demo_response(db, intent, last_user, store_id)
    result["session_id"] = None
    return result
