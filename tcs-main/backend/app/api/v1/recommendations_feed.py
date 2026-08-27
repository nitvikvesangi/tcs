"""
recommendations_feed.py — Powers the React dashboard (http://localhost:5173).
Serves GET /recommendations, POST /chat, GET /inventory, GET /promotions.
Directly backed by quick_commerce_master_synthetic_dataset.csv + ml_engine + ai_engine.
"""

from fastapi import APIRouter, Query
from typing import List, Optional, Dict, Any
import pandas as pd
import os
import sys

router = APIRouter()

def _find_csv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.abspath(os.path.join(base_dir, "..", "..", "..", "..", "..", "quick_commerce_master_synthetic_dataset.csv")),
        os.path.abspath(os.path.join(base_dir, "..", "..", "..", "..", "quick_commerce_master_synthetic_dataset.csv")),
        os.path.abspath(os.path.join(base_dir, "..", "..", "..", "quick_commerce_master_synthetic_dataset.csv")),
        os.path.abspath("quick_commerce_master_synthetic_dataset.csv"),
        "/Users/nitvik/Documents/Dev/hackathon-project/quick_commerce_master_synthetic_dataset.csv",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return "quick_commerce_master_synthetic_dataset.csv"

CSV_PATH = _find_csv()
_DF = None

def get_df():
    global _DF
    if _DF is None:
        if os.path.exists(CSV_PATH):
            _DF = pd.read_csv(CSV_PATH)
        else:
            _DF = pd.DataFrame()
    return _DF

# Try to import ML engine
_predict_action = None
try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    sys.path.insert(0, project_root)
    from ml_engine import predict_action
    _predict_action = predict_action
except Exception:
    pass

@router.get("/recommendations")
def get_recommendations(
    city: Optional[str] = None,
    dark_store_id: Optional[str] = None,
    category: Optional[str] = None,
    demand_status: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    df = get_df()
    if df.empty:
        return []

    filtered = df
    if city and city != "All":
        filtered = filtered[filtered["city"].str.lower() == city.lower()]
    if dark_store_id and dark_store_id != "All":
        filtered = filtered[filtered["dark_store_id"].str.lower() == dark_store_id.lower()]
    if category and category != "All":
        filtered = filtered[filtered["category"].str.lower() == category.lower()]
    if demand_status and demand_status != "All":
        filtered = filtered[filtered["demand_status"].str.lower() == demand_status.lower()]
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[
            filtered["product_name"].astype(str).str.lower().str.contains(q) |
            filtered["product_id"].astype(str).str.lower().str.contains(q)
        ]

    results = []
    for _, row in filtered.head(limit).iterrows():
        r = row.to_dict()
        pid = str(r.get("product_id", "P0000"))
        pname = str(r.get("product_name", "Product"))
        action = str(r.get("recommended_action", "NO PROMOTION"))
        days_exp = int(r.get("days_to_expiry", 30))
        current_stock = int(r.get("current_stock", 20))
        mrp = float(r.get("mrp", 100.0))
        disc_pct = float(r.get("current_discount_pct", 0.0))
        if disc_pct == 0 and "CLEARANCE" in action:
            disc_pct = 25.0
        elif disc_pct == 0 and "PROMOTE" in action:
            disc_pct = 15.0

        # Stockout risk
        stockout_risk = float(r.get("stockout_risk_pct", 10.0))
        if days_exp <= 2:
            risk_flag = "EXPIRY_CRITICAL"
        elif stockout_risk > 50:
            risk_flag = "STOCKOUT_RISK"
        elif float(r.get("negative_review_rate", 0.0)) > 0.4:
            risk_flag = "QUALITY_RISK"
        else:
            risk_flag = "NONE"

        exp_units = int(r.get("expected_units_with_promo", 15) or 15)
        exp_revenue = float(r.get("expected_revenue_with_promo", mrp * exp_units * (1 - disc_pct/100)) or 1000.0)
        exp_profit = float(r.get("expected_profit_with_promo", exp_revenue * 0.2) or 200.0)

        item = {
            "product_id": pid,
            "dark_store_id": str(r.get("dark_store_id", "DS-1")),
            "product_name": pname,
            "category": str(r.get("category", "General")),
            "city": str(r.get("city", "Bengaluru")),
            "current_stock": current_stock,
            "days_to_expiry": days_exp,
            "demand_status": str(r.get("demand_status", "Stable")),
            "demand_trend_pct": float(r.get("demand_trend_pct", 0.0)),
            "trend_signal": str(r.get("trend_signal", "Normal")),
            "weather_condition": str(r.get("weather_condition", "Clear")),
            "time_of_day": str(r.get("time_of_day", "Afternoon")),
            "is_weekend": bool(r.get("is_weekend", False)),
            "gross_margin_before_promo": float(r.get("gross_margin_before_promo", 20.0)),
            "competitor_price_gap_pct": float(r.get("competitor_price_gap_pct", 0.0)),
            "stockout_risk_pct": stockout_risk,
            
            # Recommendation details
            "recommended_action": action,
            "discount_pct": disc_pct,
            "explanation": f"{pname} ({pid}) recommended for {action} at {disc_pct}% discount based on {days_exp} days to expiry and {current_stock} units in stock.",
            "recommendation": {
                "action": action,
                "discount_pct": disc_pct,
                "objective": "BALANCED",
            },
            "reasons": [
                f"Days to expiry: {days_exp}",
                f"Current stock: {current_stock} units",
                f"Demand trend: {r.get('demand_trend_pct', 0.0)}%",
            ],
            "risk_flag": risk_flag,
            "options": [
                {
                    "discount_pct": disc_pct,
                    "expected_sales_units": exp_units,
                    "expected_revenue": exp_revenue,
                    "expected_profit": exp_profit,
                    "profit_impact_pct": float(r.get("profit_impact_pct", 10.0) or 10.0),
                    "inventory_reduction_pct": float(r.get("expected_inventory_reduction", 15.0) or 15.0),
                    "stockout_risk_pct": stockout_risk,
                    "expiry_waste_reduction_pct": 20.0 if days_exp < 7 else 0.0,
                    "score": 75.0,
                }
            ],
            "inventory_snapshot": {
                "stockout_urgency": "High" if stockout_risk > 50 else ("Medium" if stockout_risk > 20 else "Low"),
                "overstock_urgency": "Critical" if current_stock > 50 else "Low",
                "expiry_urgency": "Critical" if days_exp <= 2 else ("High" if days_exp <= 7 else "Low"),
                "inventory_alert_score": float(r.get("clearance_priority_score", 30) or 30),
            },
        }
        results.append(item)
    return results

@router.post("/chat")
def chat_feed(req: Dict[str, Any]):
    message = req.get("message", "") or req.get("content", "")
    try:
        from ai_engine import _call_llm
        df = get_df()
        q_lower = message.lower()
        clearance_sample = df[df["recommended_action"] == "CLEARANCE"][["product_id", "product_name", "city", "dark_store_id", "days_to_expiry", "current_stock", "mrp"]].head(4).to_dict("records")
        promote_sample = df[df["recommended_action"] == "PROMOTE"][["product_id", "product_name", "city", "dark_store_id", "demand_trend_pct", "current_stock", "mrp"]].head(4).to_dict("records")

        sys_prompt = f"""You are an AI Retail Analytics Assistant for Quick Commerce.
LIVE INVENTORY:
Clearance items: {clearance_sample}
Promote items: {promote_sample}

Answer the manager with specific product names, store IDs, stock, and rupee (₹) pricing. Never give generic boilerplate."""
        
        reply = _call_llm([{"role": "system", "content": sys_prompt}, {"role": "user", "content": message}], temperature=0.3, max_tokens=600)
        return {"response": reply, "content": reply}
    except Exception as e:
        return {"response": f"AI Assistant: {message}. (LLM key error: {e})", "content": f"AI Assistant: {message}"}

@router.get("/inventory")
def get_inventory_feed():
    recs = get_recommendations(limit=200)
    return {"total_items": len(recs), "items": recs}

@router.get("/promotions")
def get_promotions_feed():
    recs = get_recommendations(limit=200)
    return [r for r in recs if "PROMOTE" in r["recommended_action"] or "CLEARANCE" in r["recommended_action"]]
