"""Store-level inventory endpoint."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.retailer import User
from app.models.store import DarkStore
from app.schemas.inventory import InventoryWithProductOut
from app.services.inventory import InventoryService

router = APIRouter()


def _enrich(inv) -> dict:
    return {
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


@router.get("/{store_id}/inventory", response_model=List[InventoryWithProductOut], summary="Store inventory")
def store_inventory(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = db.query(DarkStore).filter(DarkStore.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if current_user.retailer_id and store.retailer_id != current_user.retailer_id:
        raise HTTPException(status_code=403, detail="Access denied")
    records = InventoryService.get_store_inventory(db, store_id, current_user.retailer_id)
    return [InventoryWithProductOut(**_enrich(r)) for r in records]
