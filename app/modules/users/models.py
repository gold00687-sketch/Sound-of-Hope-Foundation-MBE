"""
User-facing profile extensions beyond the core identity record.

The identity module owns authentication. This module owns the richer
profile data that the rest of the application references.
"""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import Gender
from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserAddress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_addresses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Uganda")
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)


class UserEmergencyContact(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_emergency_contacts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    relationship: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
