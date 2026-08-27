"""Inventory Pydantic schemas."""

import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InventoryUpdate(BaseModel):
    """
    Partial update body for PATCH /api/v1/inventory/{inventory_id}.
    All fields are optional — only supplied fields are changed.
    """
    quantity_available: Optional[int] = Field(default=None, ge=0)
    quantity_reserved: Optional[int] = Field(default=None, ge=0)
    reorder_point: Optional[int] = Field(default=None, ge=0)
    max_stock: Optional[int] = Field(default=None, ge=1)
    expiry_date: Optional[datetime.date] = None


class InventoryOut(BaseModel):
    id: int
    dark_store_id: int
    product_id: int
    quantity_available: int
    quantity_reserved: int
    reorder_point: int
    max_stock: Optional[int]
    batch_number: Optional[str]
    manufactured_date: Optional[datetime.date]
    expiry_date: Optional[datetime.date]
    last_restocked_at: Optional[datetime.datetime]
    effective_stock: int  # computed property from model
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class InventoryWithProductOut(InventoryOut):
    """Inventory record enriched with the product's catalogue fields."""
    product_sku: Optional[str] = None
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    product_mrp: Optional[float] = None
    product_shelf_life_days: Optional[int] = None
