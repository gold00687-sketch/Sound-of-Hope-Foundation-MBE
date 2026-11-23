import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import Gender, ParticipantStatus
from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Participant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A participant is a person who takes part in programmes and activities.
    They may or may not have a user account — walk-in community members
    can be registered as participants without login credentials.
    """

    __tablename__ = "participants"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ParticipantStatus.ACTIVE
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_minor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    guardian_links: Mapped[list["ParticipantGuardian"]] = relationship(
        back_populates="participant", cascade="all, delete-orphan"
    )


class ParticipantGuardian(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Links a participant to their guardian(s)."""

    __tablename__ = "participant_guardians"

    participant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    guardian_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("guardians.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    participant: Mapped["Participant"] = relationship(back_populates="guardian_links")
