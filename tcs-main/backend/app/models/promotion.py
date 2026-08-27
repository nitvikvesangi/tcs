"""
Promotion and PromotionPerformance ORM models.

Promotion stores both the recommendation metadata and the structured
`recommendation_data` JSON — the full options payload that the Promotion
Engine (Phase 4) produces.  Storing the structured JSON here means the
chatbot (Phase 5) can answer follow-up questions by reading the database,
not by regenerating from the LLM.

PromotionPerformance records actual daily performance after a promotion
is approved and running, enabling post-hoc ROI measurement.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Index, Integer, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.enums import PromotionObjective, PromotionStatus, PromotionType, RiskFlag

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.store import DarkStore
    from app.models.retailer import User


class Promotion(Base):
    """
    A promotion recommendation + its lifecycle (RECOMMENDED → APPROVED / REJECTED).

    The `recommendation_data` JSON column holds the structured options payload
    produced by the Promotion Engine — including all candidate offers and their
    simulated metrics — exactly as defined in the project contract.
    """

    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    dark_store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dark_stores.id", ondelete="CASCADE"), nullable=False
    )
    promotion_type: Mapped[PromotionType] = mapped_column(
        SAEnum(PromotionType, name="promotiontype"), nullable=False
    )
    objective: Mapped[PromotionObjective] = mapped_column(
        SAEnum(PromotionObjective, name="promotionobjective"), nullable=False
    )
    status: Mapped[PromotionStatus] = mapped_column(
        SAEnum(PromotionStatus, name="promotionstatus"),
        nullable=False,
        default=PromotionStatus.RECOMMENDED,
    )
    # The discount % of the approved / recommended option.
    discount_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    risk_flag: Mapped[RiskFlag] = mapped_column(
        SAEnum(RiskFlag, name="riskflag"), nullable=False, default=RiskFlag.NONE
    )
    # Validity window for the approved promotion.
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    # The user (retailer) who approved or rejected.
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Full structured recommendation payload (Promotion Engine output).
    # This is the JSON that the chatbot reads to answer follow-up questions.
    recommendation_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="promotions")
    dark_store: Mapped["DarkStore"] = relationship("DarkStore", back_populates="promotions")
    approved_by_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="approved_promotions", foreign_keys=[approved_by_id]
    )
    performance_records: Mapped[List["PromotionPerformance"]] = relationship(
        "PromotionPerformance", back_populates="promotion", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_promotions_store_product", "dark_store_id", "product_id"),
        Index("ix_promotions_status", "status"),
        Index("ix_promotions_created", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Promotion id={self.id} product={self.product_id} "
            f"store={self.dark_store_id} status={self.status}>"
        )


class PromotionPerformance(Base):
    """
    Daily performance record for an active Promotion.

    Populated by a background job once a promotion is APPROVED and running.
    Enables ROI measurement: planned vs actual profit/revenue/inventory impact.
    """

    __tablename__ = "promotion_performance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    promotion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("promotions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    units_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    profit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    inventory_reduction_pct: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    stockout_occurred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    promotion: Mapped["Promotion"] = relationship("Promotion", back_populates="performance_records")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PromotionPerformance promotion={self.promotion_id} date={self.date}>"
