"""
Inventory ORM model.

Each row represents one batch of a product at a specific dark store.
Multiple batches of the same product can exist at the same store (different
expiry dates). The Inventory Engine (Phase 2) aggregates across batches.

Index strategy:
  - ix_inventory_store_product: primary analytic join, covers most queries.
  - ix_inventory_expiry: used by expiry-risk queries.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.store import DarkStore
    from app.models.product import Product


class Inventory(Base):
    """Store-level, batch-level stock record."""

    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dark_store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dark_stores.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    # Physical units on shelf.
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Units locked for pending orders (not available for new orders).
    quantity_reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Alert threshold — triggers UNDERSTOCK alert when quantity_available falls below.
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Maximum storage capacity for this product at this store.
    max_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # Batch tracking — allows multiple inventory records per (store, product).
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    manufactured_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    # Null means non-perishable (shelf_life_days == 0 on the Product).
    expiry_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    # Timestamp of last restock (used for inventory aging calculations).
    last_restocked_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    dark_store: Mapped["DarkStore"] = relationship(
        "DarkStore", back_populates="inventory_items"
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="inventory_items"
    )

    __table_args__ = (
        # Primary analytic join: almost every inventory query uses both store + product.
        Index("ix_inventory_store_product", "dark_store_id", "product_id"),
        # Expiry-risk scan: "which items expire within the next N days?"
        Index("ix_inventory_expiry_date", "expiry_date"),
    )

    @property
    def effective_stock(self) -> int:
        """Available stock minus reserved stock."""
        return max(0, self.quantity_available - self.quantity_reserved)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Inventory id={self.id} store={self.dark_store_id} "
            f"product={self.product_id} qty={self.quantity_available}>"
        )
