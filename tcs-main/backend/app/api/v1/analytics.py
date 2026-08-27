"""Analytics API routes — Phase 3."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.retailer import User
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/sales", summary="Sales trend over time")
def sales(
    store_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService.sales_trend(db, current_user.retailer_id, store_id, product_id, days)


@router.get("/demand", summary="Demand forecast")
def demand(
    product_id: int = Query(...),
    store_id: int = Query(...),
    forecast_days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService.demand_forecast(db, product_id, store_id, forecast_days)


@router.get("/trends", summary="Product demand trends")
def trends(
    store_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService.product_trends(db, current_user.retailer_id, store_id, days, limit)


@router.get("/customers", summary="Customer funnel analytics")
def customers(
    store_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService.customer_analytics(db, current_user.retailer_id, store_id, days)


@router.get("/stores", summary="Store comparison")
def stores(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService.store_comparison(db, current_user.retailer_id, days)


@router.get("/top-products", summary="Top selling products")
def top_products(
    store_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService.top_products(db, current_user.retailer_id, store_id, days, limit)
