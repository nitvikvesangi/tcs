"""Promotions API routes — Phase 4."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.retailer import User
from app.schemas.promotion import (
    PromotionCompareRequest,
    PromotionHistoryItem,
    PromotionRecommendationResponse,
    PromotionRecommendRequest,
    PromotionSimulateRequest,
)
from app.schemas.simulation import ComparisonResponse, SimulationResponse
from app.services.promotion import PromotionEngine
from app.utils.enums import PromotionObjective

router = APIRouter()


@router.post(
    "/recommend",
    response_model=PromotionRecommendationResponse,
    summary="Get AI-driven promotion recommendation",
)
def recommend(
    data: PromotionRecommendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run the deterministic promotion engine + ML model + AI explanation.
    Returns 2–3 candidate options with scores, reasons, ML prediction, and AI explanation.
    """
    try:
        result = PromotionEngine.recommend(
            db,
            product_id=data.product_id,
            store_id=data.dark_store_id,
            objective=data.objective,
            max_discount_pct=data.max_discount_pct,
            min_margin_pct=data.min_margin_pct,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # --- ML Engine: RandomForest prediction -----------------------------------
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
    try:
        from ml_engine import predict_action
        from app.models.product import Product
        from app.models.inventory import Inventory as InventoryModel
        product = db.query(Product).filter(Product.id == data.product_id).first()
        inv = db.query(InventoryModel).filter(
            InventoryModel.product_id == data.product_id,
            InventoryModel.dark_store_id == data.dark_store_id
        ).first()
        ml_row = {
            "days_to_expiry": inv.expiry_date and (inv.expiry_date - __import__('datetime').date.today()).days or 60 if inv else 60,
            "current_stock": inv.quantity_available if inv else 20,
            "minimum_stock": inv.reorder_point if inv else 10,
            "maximum_stock": inv.max_stock if inv else 50,
            "stockout_risk_pct": result["inventory_snapshot"].get("inventory_alert_score", 10),
            "gross_margin_before_promo": ((float(product.mrp) - float(product.cost_price)) / float(product.mrp) * 100) if product else 20.0,
            "product_rating": float(product.base_price or 4.0) if product else 4.0,
        }
        ml_result = predict_action(ml_row)
        result["ml_prediction"] = ml_result
    except Exception as e:
        result["ml_prediction"] = {"action": "N/A", "confidence": 0.0, "probabilities": {}, "error": str(e), "fallback_used": True}

    # --- AI Engine: LLM explanation ------------------------------------------
    try:
        from ai_engine import generate_explanation, generate_risk_flag
        ai_row = {**result, "product_name": product.name if product else str(data.product_id)}
        result["ai_explanation"] = generate_explanation(ai_row)
    except Exception as e:
        result["ai_explanation"] = f"[AI explanation unavailable: {e}]"

    return result



@router.post(
    "/simulate",
    response_model=SimulationResponse,
    summary="Simulate a specific discount scenario",
)
def simulate(
    data: PromotionSimulateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return PromotionEngine.simulate(
            db,
            product_id=data.product_id,
            store_id=data.dark_store_id,
            discount_pct=data.discount_pct,
            duration_days=data.duration_days,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/compare",
    response_model=ComparisonResponse,
    summary="Compare multiple discount levels side-by-side",
)
def compare(
    data: PromotionCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = []
    for d_pct in data.discount_pcts:
        try:
            r = PromotionEngine.simulate(
                db,
                product_id=data.product_id,
                store_id=data.dark_store_id,
                discount_pct=d_pct,
                duration_days=data.duration_days,
            )
            results.append(r["result"])
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    return {
        "product_id": data.product_id,
        "dark_store_id": data.dark_store_id,
        "duration_days": data.duration_days,
        "results": results,
    }


@router.get(
    "/history",
    response_model=List[PromotionHistoryItem],
    summary="Promotion recommendation history",
)
def history(
    store_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = PromotionEngine.get_history(
        db,
        store_id=store_id,
        product_id=product_id,
        retailer_id=current_user.retailer_id,
        skip=skip,
        limit=limit,
    )
    return [PromotionHistoryItem.model_validate(r) for r in records]
