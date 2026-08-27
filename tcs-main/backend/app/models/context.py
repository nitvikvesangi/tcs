"""
Context ORM models: Weather, Festival, Trend, CompetitorPrice.

These models provide the external and market signals that the Promotion
Engine and Analytics Engine use to contextualise demand.

Weather     — daily weather at a dark store's location.
Festival    — city-level festival / public holiday with demand multiplier.
Trend       — daily demand trend score for a product (computed by ML or rule).
CompetitorPrice — competitor pricing snapshot for a product at a store.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.enums import DemandTrend, WeatherCondition

if TYPE_CHECKING:
    from app.models.store import DarkStore
    from app.models.product import Product


class Weather(Base):
    """
    Daily weather record for a dark store's location.

    One record per (dark_store, date).  The Weather API adapter (Phase 5)
    will upsert these rows.  In demo mode the data generator fills them.
    """

    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dark_store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dark_stores.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    condition: Mapped[WeatherCondition] = mapped_column(
        SAEnum(WeatherCondition, name="weathercondition"), nullable=False
    )
    temperature_c: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    humidity_pct: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    rainfall_mm: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)

    dark_store: Mapped["DarkStore"] = relationship("DarkStore", back_populates="weather_records")

    __table_args__ = (
        UniqueConstraint("dark_store_id", "date", name="uq_weather_store_date"),
        Index("ix_weather_store_date", "dark_store_id", "date"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Weather store={self.dark_store_id} date={self.date} cond={self.condition}>"


class Festival(Base):
    """
    City-level festival or public holiday.

    `demand_multiplier` is applied by the Promotion Engine to adjust expected
    demand on and around the festival date.  E.g. Diwali → 1.8×, Republic
    Day → 0.7× (delivery patterns change).
    """

    __tablename__ = "festivals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # 1.0 = no change, > 1.0 = demand increase, < 1.0 = demand decrease.
    demand_multiplier: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=1.0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_festivals_city_date", "city", "date"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Festival name={self.name!r} city={self.city!r} date={self.date}>"


class Trend(Base):
    """
    Daily demand trend snapshot for a product.

    `trend_score` is a normalised value in [0, 100] representing relative
    demand momentum.  The ML layer (Phase 3) computes this; for Phase 2 the
    data generator sets it with realistic causal logic (e.g. rain boosts
    instant-noodle trend).
    """

    __tablename__ = "trends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # 0 (no demand) – 100 (peak demand) normalised trend score.
    trend_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=50.0)
    demand_trend: Mapped[DemandTrend] = mapped_column(
        SAEnum(DemandTrend, name="demandtrend"), nullable=False, default=DemandTrend.STABLE
    )
    # Daily units sold velocity (rolling 7-day average).
    sales_velocity: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    # Aggregate search volume across all dark stores on this date.
    search_volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="trends")

    __table_args__ = (
        UniqueConstraint("product_id", "date", name="uq_trend_product_date"),
        Index("ix_trends_product_date", "product_id", "date"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Trend product={self.product_id} date={self.date} score={self.trend_score}>"


class CompetitorPrice(Base):
    """
    Competitor pricing snapshot for a product at a dark store's area.

    Captured by a scraper / manual entry.  Multiple snapshots per (product,
    store) are expected over time — the most recent one is used by the engine.
    """

    __tablename__ = "competitor_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    dark_store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dark_stores.id", ondelete="CASCADE"), nullable=False
    )
    competitor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    competitor_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # Our MRP at the time of observation (for comparison delta computation).
    our_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    recorded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship("Product", back_populates="competitor_prices")
    dark_store: Mapped["DarkStore"] = relationship("DarkStore", back_populates="competitor_prices")

    __table_args__ = (
        Index("ix_competitor_prices_product_store", "product_id", "dark_store_id"),
        Index("ix_competitor_prices_recorded_at", "recorded_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<CompetitorPrice product={self.product_id} "
            f"competitor={self.competitor_name!r} price={self.competitor_price}>"
        )
