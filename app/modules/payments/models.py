import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Records a payment made by or on behalf of a participant.

    idempotency_key prevents duplicate processing — callers must supply a
    stable key (e.g. enrolment_id + attempt number) for every payment attempt.
    Raw card numbers and CVV are never stored here.
    """

    __tablename__ = "payments"

    participant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participants.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    programme_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("programmes.id", ondelete="SET NULL"), nullable=True,
    )
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_transactions.id", ondelete="RESTRICT"),
        nullable=True, unique=True,
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="UGX")
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_payment_idempotency"),
    )
