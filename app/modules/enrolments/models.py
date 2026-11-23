import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EnrolmentStatus
from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Enrolment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Records that a participant is enrolled in a programme cohort.

    The unique constraint on (programme_id, participant_id) prevents duplicate
    enrolments at the database level regardless of application state.
    """

    __tablename__ = "enrolments"

    programme_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("programmes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cohort_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("programme_cohorts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    participant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("participants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
    )
    enrolled_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=EnrolmentStatus.ACTIVE, index=True
    )
    enrolment_date: Mapped[date] = mapped_column(Date, nullable=False)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    withdrawal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "programme_id", "participant_id",
            name="uq_enrolment_per_programme",
        ),
    )
