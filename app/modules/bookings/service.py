import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.repository import BookingRepository
from app.modules.bookings.schemas import BookingCreate, BookingStatusUpdate


class BookingService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = BookingRepository(session)

    async def create(self, data: BookingCreate) -> object:
        return await self._repo.create(data)

    async def get(self, booking_id: uuid.UUID) -> object:
        booking = await self._repo.get(booking_id)
        if not booking:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
        return booking

    async def list_bookings(
        self,
        limit: int,
        offset: int,
        act_id: str | None,
        status_filter: str | None,
    ) -> tuple[list, int]:
        return await self._repo.list(limit, offset, act_id, status_filter)

    async def update_status(self, booking_id: uuid.UUID, data: BookingStatusUpdate) -> object:
        booking = await self._repo.get(booking_id)
        if not booking:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
        return await self._repo.update_status(booking, data)
