"""DarkStore Pydantic schemas."""

import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.utils.enums import StoreStatus


class DarkStoreCreate(BaseModel):
    retailer_id: int
    name: str = Field(max_length=255)
    code: str = Field(max_length=50, description="Unique store code, e.g. DEL-DS1")
    city: str = Field(max_length=100)
    address: Optional[str] = Field(default=None, max_length=500)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: StoreStatus = StoreStatus.ACTIVE
    opening_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    closing_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")


class DarkStoreSummary(BaseModel):
    """Compact store info used in list responses."""
    id: int
    name: str
    code: str
    city: str
    status: StoreStatus

    model_config = {"from_attributes": True}


class DarkStoreOut(BaseModel):
    id: int
    retailer_id: int
    name: str
    code: str
    city: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    status: StoreStatus
    opening_time: Optional[str]
    closing_time: Optional[str]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
