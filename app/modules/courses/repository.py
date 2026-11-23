import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.courses.models import Course, CourseModule, Lesson


class CourseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, course_id: uuid.UUID) -> Course | None:
        result = await self._session.execute(
            select(Course)
            .options(selectinload(Course.modules).selectinload(CourseModule.lessons))
            .where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def list_courses(
        self, limit: int, offset: int, programme_id: uuid.UUID | None = None, is_active: bool | None = None
    ) -> tuple[list[Course], int]:
        q = select(Course)
        count_q = select(func.count()).select_from(Course)
        if programme_id:
            q = q.where(Course.programme_id == programme_id)
            count_q = count_q.where(Course.programme_id == programme_id)
        if is_active is not None:
            q = q.where(Course.is_active == is_active)
            count_q = count_q.where(Course.is_active == is_active)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(q.order_by(Course.name).limit(limit).offset(offset))
        return list(result.scalars().all()), total

    async def save(self, obj) -> None:
        self._session.add(obj)
        await self._session.flush()

    async def get_module(self, module_id: uuid.UUID) -> CourseModule | None:
        result = await self._session.execute(
            select(CourseModule).where(CourseModule.id == module_id)
        )
        return result.scalar_one_or_none()

    async def get_lesson(self, lesson_id: uuid.UUID) -> Lesson | None:
        result = await self._session.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        return result.scalar_one_or_none()
