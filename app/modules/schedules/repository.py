import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.schedules.models import ClassSession


class ScheduleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, session_id: uuid.UUID) -> ClassSession | None:
        result = await self._session.execute(
            select(ClassSession).where(ClassSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def list_for_class(
        self, class_id: uuid.UUID, from_date: date | None = None, to_date: date | None = None
    ) -> list[ClassSession]:
        q = select(ClassSession).where(ClassSession.class_id == class_id)
        if from_date:
            q = q.where(ClassSession.session_date >= from_date)
        if to_date:
            q = q.where(ClassSession.session_date <= to_date)
        result = await self._session.execute(q.order_by(ClassSession.session_date, ClassSession.start_time))
        return list(result.scalars().all())

    async def save(self, obj: ClassSession) -> ClassSession:
        self._session.add(obj)
        await self._session.flush()
        return obj
