import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Donation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "donations"

    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_transactions.id", ondelete="RESTRICT"),
        nullable=True, unique=True,
    )
    donor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    donor_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    donor_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="UGX")
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    programme_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("programmes.id", ondelete="SET NULL"), nullable=True,
    )
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
