"""
DarkStore ORM model.

A DarkStore is a physical fulfilment warehouse owned by a Retailer.
One Retailer can own multiple DarkStores across one or more cities.
Inventory is always scoped to a specific DarkStore — never city-wide.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.enums import StoreStatus

if TYPE_CHECKING:
    from app.models.retailer import Retailer
    from app.models.inventory import Inventory
    from app.models.customer import CustomerEvent
    from app.models.order import Order
    from app.models.review import Review
    from app.models.promotion import Promotion
    from app.models.context import Weather, CompetitorPrice


class DarkStore(Base):
    """Physical dark-store / warehouse operated by a Retailer."""

    __tablename__ = "dark_stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    retailer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("retailers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Human-readable store code, e.g. "DEL-DS1", "BLR-DS2" — unique across the platform.
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    status: Mapped[StoreStatus] = mapped_column(
        SAEnum(StoreStatus, name="storestatus"), nullable=False, default=StoreStatus.ACTIVE
    )
    # Optional operating-hours metadata (stored as HH:MM strings).
    opening_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    closing_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    retailer: Mapped["Retailer"] = relationship("Retailer", back_populates="dark_stores")
    inventory_items: Mapped[List["Inventory"]] = relationship(
        "Inventory", back_populates="dark_store", cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="dark_store"
    )
    customer_events: Mapped[List["CustomerEvent"]] = relationship(
        "CustomerEvent", back_populates="dark_store"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="dark_store"
    )
    promotions: Mapped[List["Promotion"]] = relationship(
        "Promotion", back_populates="dark_store"
    )
    weather_records: Mapped[List["Weather"]] = relationship(
        "Weather", back_populates="dark_store", cascade="all, delete-orphan"
    )
    competitor_prices: Mapped[List["CompetitorPrice"]] = relationship(
        "CompetitorPrice", back_populates="dark_store"
    )

    # Composite indexes for common analytic queries.
    __table_args__ = (
        Index("ix_dark_stores_retailer_city", "retailer_id", "city"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DarkStore id={self.id} code={self.code!r} city={self.city!r}>"
