import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.events.models import Event, EventRegistration


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, event_id: uuid.UUID) -> Event | None:
        result = await self._session.execute(select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()

    async def list_events(
        self, limit: int, offset: int,
        is_public: bool | None = None,
        from_date: datetime | None = None,
    ) -> tuple[list[Event], int]:
        q = select(Event)
        count_q = select(func.count()).select_from(Event)
        if is_public is not None:
            q = q.where(Event.is_public == is_public)
            count_q = count_q.where(Event.is_public == is_public)
        if from_date:
            q = q.where(Event.starts_at >= from_date)
            count_q = count_q.where(Event.starts_at >= from_date)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Event.starts_at.asc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, obj) -> None:
        self._session.add(obj)
        await self._session.flush()

    async def list_registrations(self, event_id: uuid.UUID) -> list[EventRegistration]:
        result = await self._session.execute(
            select(EventRegistration).where(EventRegistration.event_id == event_id)
        )
        return list(result.scalars().all())

    async def count_registrations(self, event_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(EventRegistration)
            .where(EventRegistration.event_id == event_id)
        )
        return result.scalar_one()
