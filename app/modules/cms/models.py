import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import PublishStatus
from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Page(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cms_pages"

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    meta_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=PublishStatus.DRAFT, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    versions: Mapped[list["PageVersion"]] = relationship(
        back_populates="page", cascade="all, delete-orphan", order_by="PageVersion.version_number"
    )


class PageVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cms_page_versions"

    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cms_pages.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    version_number: Mapped[int] = mapped_column(nullable=False)
    content_blocks: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False,
    )

    page: Mapped["Page"] = relationship(back_populates="versions")

    __table_args__ = (
        UniqueConstraint("page_id", "version_number", name="uq_page_version"),
    )
