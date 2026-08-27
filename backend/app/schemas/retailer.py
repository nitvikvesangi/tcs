"""Retailer Pydantic schemas."""

import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RetailerCreate(BaseModel):
    name: str = Field(max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    city: Optional[str] = Field(default=None, max_length=100)


class RetailerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    city: Optional[str]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
