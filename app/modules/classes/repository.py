import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.classes.models import Class


class ClassRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, class_id: uuid.UUID) -> Class | None:
        result = await self._session.execute(select(Class).where(Class.id == class_id))
        return result.scalar_one_or_none()

    async def list_classes(
        self, limit: int, offset: int,
        course_id: uuid.UUID | None = None,
        cohort_id: uuid.UUID | None = None,
        instructor_id: uuid.UUID | None = None,
    ) -> tuple[list[Class], int]:
        q = select(Class)
        count_q = select(func.count()).select_from(Class)
        for col, val in [
            (Class.course_id, course_id),
            (Class.cohort_id, cohort_id),
            (Class.instructor_id, instructor_id),
        ]:
            if val is not None:
                q = q.where(col == val)
                count_q = count_q.where(col == val)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Class.start_date.desc().nullslast()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, obj: Class) -> Class:
        self._session.add(obj)
        await self._session.flush()
        return obj
