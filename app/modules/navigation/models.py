import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class NavigationMenu(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "navigation_menus"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)

    items: Mapped[list["NavigationItem"]] = relationship(
        back_populates="menu", cascade="all, delete-orphan", order_by="NavigationItem.order"
    )


class NavigationItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "navigation_items"

    menu_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("navigation_menus.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("navigation_items.id", ondelete="CASCADE"), nullable=True,
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cms_pages.id", ondelete="SET NULL"), nullable=True,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    target: Mapped[str] = mapped_column(String(20), nullable=False, default="_self")

    menu: Mapped["NavigationMenu"] = relationship(back_populates="items")
