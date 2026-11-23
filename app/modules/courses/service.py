import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.courses.models import Course, CourseModule, Lesson
from app.modules.courses.repository import CourseRepository
from app.modules.courses.schemas import CourseCreate, CourseUpdate, LessonCreate, ModuleCreate


class CourseService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CourseRepository(session)

    async def create(self, data: CourseCreate) -> Course:
        course = Course(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(course)
        return course

    async def get(self, course_id: uuid.UUID) -> Course:
        c = await self._repo.get_by_id(course_id)
        if c is None:
            raise NotFoundError("Course not found.")
        return c

    async def list_courses(self, limit: int, offset: int, programme_id: uuid.UUID | None, is_active: bool | None):
        return await self._repo.list_courses(limit, offset, programme_id, is_active)

    async def update(self, course_id: uuid.UUID, data: CourseUpdate) -> Course:
        c = await self._repo.get_by_id(course_id)
        if c is None:
            raise NotFoundError("Course not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(c, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(c)
        return c

    async def add_module(self, course_id: uuid.UUID, data: ModuleCreate) -> CourseModule:
        c = await self._repo.get_by_id(course_id)
        if c is None:
            raise NotFoundError("Course not found.")
        module = CourseModule(course_id=course_id, **data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(module)
        return module

    async def add_lesson(self, module_id: uuid.UUID, data: LessonCreate) -> Lesson:
        m = await self._repo.get_module(module_id)
        if m is None:
            raise NotFoundError("Module not found.")
        lesson = Lesson(module_id=module_id, **data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(lesson)
        return lesson

    async def publish_lesson(self, lesson_id: uuid.UUID) -> Lesson:
        lesson = await self._repo.get_lesson(lesson_id)
        if lesson is None:
            raise NotFoundError("Lesson not found.")
        lesson.is_published = True
        async with atomic(self._repo._session):
            await self._repo.save(lesson)
        return lesson
