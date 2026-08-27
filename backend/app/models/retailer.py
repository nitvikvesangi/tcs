"""
Retailer and User ORM models.

Retailer is the top-level business entity that owns one or more DarkStores.
User belongs to a Retailer and authenticates via JWT (see app/core/security.py).
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.enums import UserRole

if TYPE_CHECKING:
    from app.models.store import DarkStore
    from app.models.promotion import Promotion


class Retailer(Base):
    """Top-level business entity. Owns users and dark stores."""

    __tablename__ = "retailers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="retailer", cascade="all, delete-orphan"
    )
    dark_stores: Mapped[List["DarkStore"]] = relationship(
        "DarkStore", back_populates="retailer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Retailer id={self.id} name={self.name!r}>"


class User(Base):
    """Platform user — always scoped to a Retailer (for this product)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole"),
        nullable=False,
        default=UserRole.RETAILER_ADMIN,
    )
    retailer_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("retailers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    retailer: Mapped[Optional["Retailer"]] = relationship(
        "Retailer", back_populates="users"
    )
    approved_promotions: Mapped[List["Promotion"]] = relationship(
        "Promotion",
        back_populates="approved_by_user",
        foreign_keys="Promotion.approved_by_id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
