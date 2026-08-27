"""
Review ORM model.

Customer-written product reviews, optionally linked to a specific Order.
The ML layer (Phase 3) will compute sentiment_score from the text; for now
it is stored as a float set by the data generator or a future NLP call.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.product import Product
    from app.models.store import DarkStore
    from app.models.order import Order


class Review(Base):
    """Customer product review with optional NLP sentiment score."""

    __tablename__ = "reviews"

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
    # Nullable — a review can exist without a linked order (e.g. imported legacy data).
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )
    # Star rating 1–5.
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Sentiment score: -1.0 (very negative) to +1.0 (very positive).
    # NULL until Phase 3 ML analysis populates it.
    sentiment_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="reviews")
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    dark_store: Mapped["DarkStore"] = relationship("DarkStore", back_populates="reviews")
    order: Mapped[Optional["Order"]] = relationship("Order")

    __table_args__ = (
        Index("ix_reviews_product_id", "product_id"),
        Index("ix_reviews_store_id", "dark_store_id"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Review id={self.id} product={self.product_id} rating={self.rating}>"
