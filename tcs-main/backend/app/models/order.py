"""
Order and OrderItem ORM models.

Order is the transaction record for a customer purchase at a dark store.
OrderItem is the per-product line within an order.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.enums import OrderStatus

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.store import DarkStore
    from app.models.product import Product


class Order(Base):
    """Transaction record — one order per customer visit / delivery."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dark_store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dark_stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="orderstatus"), nullable=False, default=OrderStatus.PLACED
    )
    # INR amounts.
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    placed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    delivered_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    dark_store: Mapped["DarkStore"] = relationship("DarkStore", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Analytics: sales by store over time.
        Index("ix_orders_store_placed", "dark_store_id", "placed_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Order id={self.id} status={self.status} total={self.total_amount}>"


class OrderItem(Base):
    """Single product line within an Order."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # MRP at the time of purchase (prices can change).
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # Promotion discount applied to this line item (0 if no promotion).
    discount_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    total_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")

    __table_args__ = (
        # Needed for product sales analytics.
        Index("ix_order_items_product", "product_id"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OrderItem id={self.id} product={self.product_id} qty={self.quantity}>"
