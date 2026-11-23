import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import MusicianBooking
from app.modules.bookings.schemas import BookingCreate, BookingStatusUpdate


class BookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: BookingCreate) -> MusicianBooking:
        booking = MusicianBooking(**data.model_dump())
        self._session.add(booking)
        await self._session.flush()
        await self._session.refresh(booking)
        return booking

    async def get(self, booking_id: uuid.UUID) -> MusicianBooking | None:
        result = await self._session.execute(
            select(MusicianBooking).where(MusicianBooking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        limit: int,
        offset: int,
        act_id: str | None = None,
        status: str | None = None,
    ) -> tuple[list[MusicianBooking], int]:
        q = select(MusicianBooking)
        if act_id:
            q = q.where(MusicianBooking.act_id == act_id)
        if status:
            q = q.where(MusicianBooking.status == status)
        total_q = select(func.count()).select_from(q.subquery())
        total = (await self._session.execute(total_q)).scalar_one()
        q = q.order_by(MusicianBooking.created_at.desc()).limit(limit).offset(offset)
        rows = (await self._session.execute(q)).scalars().all()
        return list(rows), total

    async def update_status(
        self, booking: MusicianBooking, data: BookingStatusUpdate
    ) -> MusicianBooking:
        booking.status = data.status
        if data.internal_notes is not None:
            booking.internal_notes = data.internal_notes
        if data.status == "confirmed" and booking.confirmed_at is None:
            booking.confirmed_at = datetime.now(UTC)
        elif data.status == "cancelled" and booking.cancelled_at is None:
            booking.cancelled_at = datetime.now(UTC)
        await self._session.flush()
        await self._session.refresh(booking)
        return booking
