import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.events.models import Event, EventRegistration
from app.modules.events.repository import EventRepository
from app.modules.events.schemas import EventCreate, EventUpdate, RegistrationCreate


class EventService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = EventRepository(session)

    async def create(self, data: EventCreate, created_by_id: uuid.UUID) -> Event:
        event = Event(**data.model_dump(), created_by_id=created_by_id)
        async with atomic(self._repo._session):
            await self._repo.save(event)
        return event

    async def get(self, event_id: uuid.UUID) -> Event:
        e = await self._repo.get_by_id(event_id)
        if e is None:
            raise NotFoundError("Event not found.")
        return e

    async def list_events(self, limit: int, offset: int, is_public: bool | None, from_date):
        return await self._repo.list_events(limit, offset, is_public, from_date)

    async def update(self, event_id: uuid.UUID, data: EventUpdate) -> Event:
        e = await self._repo.get_by_id(event_id)
        if e is None:
            raise NotFoundError("Event not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(e, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(e)
        return e

    async def publish(self, event_id: uuid.UUID) -> Event:
        e = await self._repo.get_by_id(event_id)
        if e is None:
            raise NotFoundError("Event not found.")
        e.is_published = True
        async with atomic(self._repo._session):
            await self._repo.save(e)
        return e

    async def register(self, event_id: uuid.UUID, data: RegistrationCreate) -> EventRegistration:
        e = await self._repo.get_by_id(event_id)
        if e is None:
            raise NotFoundError("Event not found.")
        if not e.is_published:
            raise ValidationError("This event is not open for registration.")
        if e.max_attendees is not None:
            count = await self._repo.count_registrations(event_id)
            if count >= e.max_attendees:
                raise ValidationError("This event has reached capacity.")
        reg = EventRegistration(event_id=event_id, **data.model_dump())
        try:
            async with atomic(self._repo._session):
                await self._repo.save(reg)
        except IntegrityError:
            raise ConflictError("Already registered for this event.")
        return reg

    async def list_registrations(self, event_id: uuid.UUID) -> list[EventRegistration]:
        return await self._repo.list_registrations(event_id)
