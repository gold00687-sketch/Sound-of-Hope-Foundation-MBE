import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Discussion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "discussions"

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    context_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    context_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    comments: Mapped[list["DiscussionComment"]] = relationship(
        back_populates="discussion", cascade="all, delete-orphan"
    )


class DiscussionComment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "discussion_comments"

    discussion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_removed: Mapped[bool] = mapped_column(default=False, nullable=False)

    discussion: Mapped["Discussion"] = relationship(back_populates="comments")
