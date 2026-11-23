import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ConsentRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Records that a participant (or their guardian) has given informed consent
    for a specific activity or data processing purpose.
    """

    __tablename__ = "consent_records"

    participant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participants.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("guardians.id", ondelete="SET NULL"),
        nullable=True,
    )
    consent_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    given_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
