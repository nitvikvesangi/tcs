"""
recommendations_feed.py — Powers the React dashboard (http://localhost:5173).
Serves GET /recommendations, POST /chat, GET /inventory, GET /promotions.
Directly backed by quick_commerce_master_synthetic_dataset.csv + ml_engine (batch) + ai_engine.
"""

from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
import pandas as pd
import os
import sys

router = APIRouter()

# ── Hardcoded project root (works regardless of uvicorn launch dir) ──────────
PROJECT_ROOT = "/Users/nitvik/Documents/Dev/hackathon-project"
CSV_PATH = os.path.join(PROJECT_ROOT, "quick_commerce_master_synthetic_dataset.csv")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Cache: load CSV + batch ML predictions ONCE at startup ───────────────────
_FULL_DF: Optional[pd.DataFrame] = None   # raw CSV
_PRED_DF: Optional[pd.DataFrame] = None   # CSV + ml_predicted_action column


def _load_data():
    global _FULL_DF, _PRED_DF
    if _PRED_DF is not None:
        return _PRED_DF

    # 1. Load CSV
    df = pd.read_csv(CSV_PATH)
    _FULL_DF = df

    # 2. Batch ML prediction (one call for all 10 000 rows)
    try:
        from ml_engine import predict_batch
        actions = predict_batch(df)
        df = df.copy()
        df["ml_action"] = actions
    except Exception:
        # Fallback: use CSV ground-truth column
        df["ml_action"] = df.get("recommended_action", "NO PROMOTION")

    _PRED_DF = df
    return _PRED_DF


# Pre-load at import time so the first request is instant
try:
    _load_data()
except Exception:
    pass


def _row_to_item(r: dict) -> dict:
    """Convert one annotated CSV row into the React Recommendation shape."""
    pid          = str(r.get("product_id", "P0000"))
    pname        = str(r.get("product_name", "Product"))
    days_exp     = int(r.get("days_to_expiry", 30))
    stock        = int(r.get("current_stock", 20))
    mrp          = float(r.get("mrp", 100.0))
    action       = str(r.get("ml_action", r.get("recommended_action", "NO PROMOTION")))
    stockout_pct = float(r.get("stockout_risk_pct", 10.0))
    neg_review   = float(r.get("negative_review_rate", 0.0))

    # Discount %
    disc = float(r.get("current_discount_pct", 0.0))
    if disc == 0:
        if "CLEARANCE" in action:
            disc = 25.0
        elif "PROMOTE" in action:
            disc = 15.0
        elif "COMPETITIVE" in action:
            disc = 10.0

    # Risk flag
    if days_exp <= 2:
        risk_flag = "EXPIRY_CRITICAL"
    elif stockout_pct > 50:
        risk_flag = "STOCKOUT_RISK"
    elif neg_review > 0.4:
        risk_flag = "QUALITY_RISK"
    else:
        risk_flag = "NONE"

    exp_units   = int(r.get("expected_units_with_promo", 15) or 15)
    exp_revenue = float(r.get("expected_revenue_with_promo", mrp * exp_units * (1 - disc / 100)) or 1000.0)
    exp_profit  = float(r.get("expected_profit_with_promo", exp_revenue * 0.2) or 200.0)

    return {
        "product_id":              pid,
        "dark_store_id":           str(r.get("dark_store_id", "DS-1")),
        "product_name":            pname,
        "category":                str(r.get("category", "General")),
        "city":                    str(r.get("city", "Bengaluru")),
        "current_stock":           stock,
        "days_to_expiry":          days_exp,
        "demand_status":           str(r.get("demand_status", "Stable")),
        "demand_trend_pct":        float(r.get("demand_trend_pct", 0.0)),
        "trend_signal":            str(r.get("trend_signal", "Normal")),
        "weather_condition":       str(r.get("weather_condition", "Clear")),
        "time_of_day":             str(r.get("time_of_day", "Afternoon")),
        "is_weekend":              bool(r.get("is_weekend", False)),
        "gross_margin_before_promo": float(r.get("gross_margin_before_promo", 20.0)),
        "competitor_price_gap_pct":  float(r.get("competitor_price_gap_pct", 0.0)),
        "stockout_risk_pct":       stockout_pct,
        "recommended_action":      action,
        "discount_pct":            disc,
        "explanation": (
            f"{pname} ({pid}) → {action} at {disc:.0f}% discount. "
            f"Stock: {stock} units | Expiry: {days_exp} days | "
            f"Demand: {r.get('demand_trend_pct', 0.0)}%"
        ),
        "recommendation": {"action": action, "discount_pct": disc, "objective": "BALANCED"},
        "reasons": [
            f"Days to expiry: {days_exp}",
            f"Current stock: {stock} units",
            f"Demand trend: {r.get('demand_trend_pct', 0.0)}%",
            f"Stockout risk: {stockout_pct:.1f}%",
        ],
        "risk_flag": risk_flag,
        "options": [{
            "discount_pct":              disc,
            "expected_sales_units":      exp_units,
            "expected_revenue":          exp_revenue,
            "expected_profit":           exp_profit,
            "profit_impact_pct":         float(r.get("profit_impact_pct", 10.0) or 10.0),
            "inventory_reduction_pct":   float(r.get("expected_inventory_reduction", 15.0) or 15.0),
            "stockout_risk_pct":         stockout_pct,
            "expiry_waste_reduction_pct": 20.0 if days_exp < 7 else 0.0,
            "score": 75.0,
        }],
        "inventory_snapshot": {
            "stockout_urgency":   "High" if stockout_pct > 50 else ("Medium" if stockout_pct > 20 else "Low"),
            "overstock_urgency":  "Critical" if stock > 50 else "Low",
            "expiry_urgency":     "Critical" if days_exp <= 2 else ("High" if days_exp <= 7 else "Low"),
            "inventory_alert_score": float(r.get("clearance_priority_score", 30) or 30),
        },
    }


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/recommendations")
def get_recommendations(
    city:          Optional[str] = None,
    dark_store_id: Optional[str] = None,
    category:      Optional[str] = None,
    demand_status: Optional[str] = None,
    search_query:  Optional[str] = None,
    limit:         int = Query(10000, ge=1, le=10000),
):
    df = _load_data()
    if df is None or df.empty:
        return []

    mask = pd.Series([True] * len(df), index=df.index)

    if city and city not in ("All", "all", ""):
        mask &= df["city"].str.lower() == city.lower()
    if dark_store_id and dark_store_id not in ("All", "all", ""):
        mask &= df["dark_store_id"].str.lower() == dark_store_id.lower()
    if category and category not in ("All", "all", ""):
        mask &= df["category"].str.lower() == category.lower()
    if demand_status and demand_status not in ("All", "all", ""):
        mask &= df["demand_status"].str.lower() == demand_status.lower()
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        mask &= (
            df["product_name"].astype(str).str.lower().str.contains(q) |
            df["product_id"].astype(str).str.lower().str.contains(q)
        )

    filtered = df[mask].head(limit)
    return [_row_to_item(r) for r in filtered.to_dict("records")]


@router.post("/chat")
def chat_feed(req: Dict[str, Any]):
    message = req.get("message", "") or req.get("content", "")
    try:
        from ai_engine import _call_llm
        df = _load_data()
        clearance = df[df["ml_action"] == "CLEARANCE"][
            ["product_id", "product_name", "city", "dark_store_id", "days_to_expiry", "current_stock", "mrp"]
        ].head(4).to_dict("records")
        promote = df[df["ml_action"] == "PROMOTE"][
            ["product_id", "product_name", "city", "dark_store_id", "demand_trend_pct", "current_stock", "mrp"]
        ].head(4).to_dict("records")

        sys_prompt = (
            "You are an AI Retail Analytics Assistant for Quick Commerce.\n"
            f"LIVE INVENTORY:\nClearance items (urgent): {clearance}\nPromote items (high demand): {promote}\n\n"
            "Answer the manager with specific product names, store IDs, stock, and ₹ pricing. "
            "Never give generic boilerplate."
        )
        reply = _call_llm(
            [{"role": "system", "content": sys_prompt}, {"role": "user", "content": message}],
            temperature=0.3,
            max_tokens=600,
        )
        return {"answer": reply, "response": reply, "content": reply}
    except Exception as e:
        return {"answer": f"AI error: {e}", "response": f"AI error: {e}", "content": f"AI error: {e}"}


@router.get("/inventory")
def get_inventory_feed():
    recs = get_recommendations(limit=10000)
    return {"total_items": len(recs), "items": recs}


@router.get("/promotions")
def get_promotions_feed():
    recs = get_recommendations(limit=10000)
    return [r for r in recs if "PROMOTE" in r["recommended_action"] or "CLEARANCE" in r["recommended_action"]]
