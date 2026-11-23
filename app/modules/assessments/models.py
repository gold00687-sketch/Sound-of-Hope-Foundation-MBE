import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Assessment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assessments"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="assignment")
    max_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=100)
    passing_score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    submissions: Mapped[list["AssessmentSubmission"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class AssessmentSubmission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assessment_submissions"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    participant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    graded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    assessment: Mapped["Assessment"] = relationship(back_populates="submissions")

    __table_args__ = (
        UniqueConstraint("assessment_id", "participant_id", name="uq_submission_per_assessment"),
    )
