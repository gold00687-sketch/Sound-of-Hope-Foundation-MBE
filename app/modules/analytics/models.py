import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, UUIDPrimaryKeyMixin


class MetricSnapshot(Base, UUIDPrimaryKeyMixin):
    """Periodic snapshot of key organisational metrics for dashboards."""

    __tablename__ = "metric_snapshots"

    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    dimensions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
