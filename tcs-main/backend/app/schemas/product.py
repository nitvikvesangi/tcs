"""Product Pydantic schemas."""

import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str = Field(max_length=50, description="Business identifier, e.g. P0059")
    name: str = Field(max_length=255)
    category: str = Field(max_length=100)
    subcategory: Optional[str] = Field(default=None, max_length=100)
    brand: Optional[str] = Field(default=None, max_length=100)
    unit: Optional[str] = Field(default=None, max_length=50)
    mrp: float = Field(gt=0, description="Maximum Retail Price in INR")
    cost_price: float = Field(gt=0, description="Landed cost in INR")
    shelf_life_days: int = Field(ge=0, description="0 means non-perishable")
    description: Optional[str] = None


class ProductSummary(BaseModel):
    """Compact product info for list responses and nested references."""
    id: int
    sku: str
    name: str
    category: str
    mrp: float

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    subcategory: Optional[str]
    brand: Optional[str]
    unit: Optional[str]
    mrp: float
    cost_price: float
    shelf_life_days: int
    description: Optional[str]
    is_active: bool
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
