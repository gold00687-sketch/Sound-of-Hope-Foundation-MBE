import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import AttendanceStatus
from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AttendanceRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Records whether a participant attended a specific class session.
    One record per participant per session — enforced at DB level.
    """

    __tablename__ = "attendance_records"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("class_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    participant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    recorded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AttendanceStatus.PRESENT
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("session_id", "participant_id", name="uq_attendance_per_session"),
    )
