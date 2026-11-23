import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MessageThread(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "message_threads"

    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    messages: Mapped[list["Message"]] = relationship(
        back_populates="thread", cascade="all, delete-orphan"
    )


class ThreadParticipant(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "thread_participants"

    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message_threads.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    __table_args__ = (UniqueConstraint("thread_id", "user_id"),)


class Message(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "messages"

    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message_threads.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_removed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    thread: Mapped["MessageThread"] = relationship(back_populates="messages")
