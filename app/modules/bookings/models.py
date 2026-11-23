import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MusicianBooking(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Records a public musician booking enquiry submitted via the website.

    act_id is the frontend slug (e.g. "lufafa-noah", "orchestra", "live-band").
    Raw card details are never stored here.
    """

    __tablename__ = "musician_bookings"

    act_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    act_name: Mapped[str] = mapped_column(String(255), nullable=False)
    booker_name: Mapped[str] = mapped_column(String(255), nullable=False)
    booker_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    booker_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_location: Mapped[str] = mapped_column(String(255), nullable=False)
    guest_count: Mapped[int | None] = mapped_column(nullable=True)
    duration_hours: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    fee_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    fee_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    # status values: "pending" | "confirmed" | "cancelled"
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
