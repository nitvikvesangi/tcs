"""
Customer and CustomerEvent ORM models.

Customer is scoped to a Retailer (they registered/shopped with that retailer).
CustomerEvent tracks all funnel actions: VIEW → SEARCH → CART_ADD → PURCHASE.

Index strategy:
  - (customer_id, event_type): customer funnel analysis.
  - (product_id, event_type): product engagement analytics.
  - (dark_store_id, created_at): store-level timeline queries.
  - (customer_id, product_id): repeat-purchase and conversion-rate queries.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.enums import CustomerEventType, CustomerSegment

if TYPE_CHECKING:
    from app.models.retailer import Retailer
    from app.models.store import DarkStore
    from app.models.product import Product
    from app.models.order import Order
    from app.models.review import Review


class Customer(Base):
    """End consumer — scoped to a Retailer, shops across multiple DarkStores."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    retailer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("retailers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # External app/POS identifier — preserves PII-free linkage.
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    segment: Mapped[CustomerSegment] = mapped_column(
        SAEnum(CustomerSegment, name="customersegment"),
        nullable=False,
        default=CustomerSegment.NEW_CUSTOMER,
    )
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    retailer: Mapped["Retailer"] = relationship("Retailer")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")
    events: Mapped[List["CustomerEvent"]] = relationship(
        "CustomerEvent", back_populates="customer", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="customer")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Customer id={self.id} segment={self.segment}>"


class CustomerEvent(Base):
    """
    Single funnel action: VIEW, SEARCH, CART_ADD, or PURCHASE.

    Every digital touch-point the customer has with a product at a specific store
    is recorded here.  This table feeds the Analytics Engine (Phase 3).
    """

    __tablename__ = "customer_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    dark_store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dark_stores.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[CustomerEventType] = mapped_column(
        SAEnum(CustomerEventType, name="customereventtype"), nullable=False
    )
    # Groups events within the same shopping session.
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Only populated for SEARCH events.
    search_query: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="events")
    product: Mapped["Product"] = relationship("Product", back_populates="customer_events")
    dark_store: Mapped["DarkStore"] = relationship("DarkStore", back_populates="customer_events")

    __table_args__ = (
        Index("ix_ce_customer_event_type", "customer_id", "event_type"),
        Index("ix_ce_product_event_type", "product_id", "event_type"),
        Index("ix_ce_store_created", "dark_store_id", "created_at"),
        Index("ix_ce_customer_product", "customer_id", "product_id"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CustomerEvent id={self.id} type={self.event_type}>"
