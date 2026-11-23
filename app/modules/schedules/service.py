import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.schedules.models import ClassSession
from app.modules.schedules.repository import ScheduleRepository
from app.modules.schedules.schemas import SessionCreate


class ScheduleService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ScheduleRepository(session)

    async def create_session(self, data: SessionCreate) -> ClassSession:
        s = ClassSession(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(s)
        return s

    async def get_session(self, session_id: uuid.UUID) -> ClassSession:
        s = await self._repo.get_by_id(session_id)
        if s is None:
            raise NotFoundError("Session not found.")
        return s

    async def list_for_class(
        self, class_id: uuid.UUID, from_date: date | None = None, to_date: date | None = None
    ) -> list[ClassSession]:
        return await self._repo.list_for_class(class_id, from_date, to_date)

    async def cancel_session(self, session_id: uuid.UUID, reason: str | None) -> ClassSession:
        s = await self._repo.get_by_id(session_id)
        if s is None:
            raise NotFoundError("Session not found.")
        if s.is_cancelled:
            raise ValidationError("Session is already cancelled.")
        s.is_cancelled = True
        s.cancellation_reason = reason
        async with atomic(self._repo._session):
            await self._repo.save(s)
        return s
