"""
Product ORM model.

Products are catalogue-level entities — not store-specific.
Store-specific quantities, expiry dates, and reorder points live in Inventory.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.inventory import Inventory
    from app.models.customer import CustomerEvent
    from app.models.order import OrderItem
    from app.models.review import Review
    from app.models.promotion import Promotion
    from app.models.context import Trend, CompetitorPrice


class Product(Base):
    """Catalogue-level product — shared across all dark stores."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # SKU is the business identifier used in API responses (e.g. "P0059").
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Selling unit, e.g. "500g", "1L", "piece".
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # Maximum Retail Price in INR.
    mrp: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # Cost price (landed cost) — used for margin/profit calculations.
    cost_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # Shelf life in days (0 = non-perishable / no expiry tracking).
    shelf_life_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    inventory_items: Mapped[List["Inventory"]] = relationship(
        "Inventory", back_populates="product"
    )
    customer_events: Mapped[List["CustomerEvent"]] = relationship(
        "CustomerEvent", back_populates="product"
    )
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="product"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="product"
    )
    promotions: Mapped[List["Promotion"]] = relationship(
        "Promotion", back_populates="product"
    )
    trends: Mapped[List["Trend"]] = relationship(
        "Trend", back_populates="product", cascade="all, delete-orphan"
    )
    competitor_prices: Mapped[List["CompetitorPrice"]] = relationship(
        "CompetitorPrice", back_populates="product"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Product id={self.id} sku={self.sku!r} name={self.name!r}>"
