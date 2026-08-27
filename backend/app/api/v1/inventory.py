"""Inventory API routes — Phase 2."""

import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.retailer import User
from app.schemas.alerts import AlertsResponse, InventoryAlert
from app.schemas.inventory import InventoryOut, InventoryUpdate, InventoryWithProductOut
from app.services.inventory import InventoryService, calc_effective_stock
from app.utils.enums import InventoryAlertType, UrgencyLevel

router = APIRouter()


def _enrich(inv) -> dict:
    base = {
        "id": inv.id,
        "dark_store_id": inv.dark_store_id,
        "product_id": inv.product_id,
        "quantity_available": inv.quantity_available,
        "quantity_reserved": inv.quantity_reserved,
        "reorder_point": inv.reorder_point,
        "max_stock": inv.max_stock,
        "batch_number": inv.batch_number,
        "manufactured_date": inv.manufactured_date,
        "expiry_date": inv.expiry_date,
        "last_restocked_at": inv.last_restocked_at,
        "effective_stock": inv.effective_stock,
        "created_at": inv.created_at,
        "updated_at": inv.updated_at,
        "product_sku": inv.product.sku if inv.product else None,
        "product_name": inv.product.name if inv.product else None,
        "product_category": inv.product.category if inv.product else None,
        "product_mrp": float(inv.product.mrp) if inv.product else None,
        "product_shelf_life_days": inv.product.shelf_life_days if inv.product else None,
    }
    return base


@router.get("", response_model=List[InventoryWithProductOut], summary="List inventory")
def list_inventory(
    store_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = InventoryService.get_all_inventory(
        db,
        retailer_id=current_user.retailer_id,
        store_id=store_id,
        skip=skip,
        limit=limit,
    )
    return [InventoryWithProductOut(**_enrich(r)) for r in records]


@router.get("/alerts", response_model=AlertsResponse, summary="Get inventory alerts")
def get_alerts(
    store_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw = InventoryService.get_alerts(db, retailer_id=current_user.retailer_id, store_id=store_id)
    critical = sum(1 for a in raw if a["urgency"] == UrgencyLevel.CRITICAL)
    high = sum(1 for a in raw if a["urgency"] == UrgencyLevel.HIGH)
    alerts = [
        InventoryAlert(
            store_id=a["store_id"],
            store_code=a["store_code"],
            product_id=a["product_id"],
            product_sku=a["product_sku"],
            product_name=a["product_name"],
            alert_type=a["alert_type"],
            urgency=a["urgency"],
            message=a["message"],
            details=a.get("details", {}),
        )
        for a in raw
    ]
    return AlertsResponse(
        store_id=store_id,
        total_alerts=len(alerts),
        critical_count=critical,
        high_count=high,
        alerts=alerts,
        generated_at=datetime.datetime.now(datetime.timezone.utc),
    )


@router.get("/{inventory_id}", response_model=InventoryWithProductOut, summary="Get single inventory record")
def get_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = InventoryService.get_inventory_by_id(db, inventory_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return InventoryWithProductOut(**_enrich(inv))


@router.patch("/{inventory_id}", response_model=InventoryWithProductOut, summary="Update inventory quantities")
def update_inventory(
    inventory_id: int,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = InventoryService.get_inventory_by_id(db, inventory_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    updates = data.model_dump(exclude_none=True)
    inv = InventoryService.update_inventory(db, inv, updates)
    return InventoryWithProductOut(**_enrich(inv))
