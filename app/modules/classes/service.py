import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.classes.models import Class
from app.modules.classes.repository import ClassRepository
from app.modules.classes.schemas import ClassCreate, ClassUpdate


class ClassService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ClassRepository(session)

    async def create(self, data: ClassCreate) -> Class:
        cls = Class(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(cls)
        return cls

    async def get(self, class_id: uuid.UUID) -> Class:
        c = await self._repo.get_by_id(class_id)
        if c is None:
            raise NotFoundError("Class not found.")
        return c

    async def list_classes(self, limit: int, offset: int, course_id: uuid.UUID | None,
                           cohort_id: uuid.UUID | None, instructor_id: uuid.UUID | None):
        return await self._repo.list_classes(limit, offset, course_id, cohort_id, instructor_id)

    async def update(self, class_id: uuid.UUID, data: ClassUpdate) -> Class:
        c = await self._repo.get_by_id(class_id)
        if c is None:
            raise NotFoundError("Class not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(c, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(c)
        return c
