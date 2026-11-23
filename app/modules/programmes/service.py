import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.programmes.models import Programme, ProgrammeCategory, ProgrammeCohort
from app.modules.programmes.repository import CategoryRepository, ProgrammeRepository
from app.modules.programmes.schemas import (
    CohortCreate,
    ProgrammeCategoryCreate,
    ProgrammeCreate,
    ProgrammeUpdate,
)


class ProgrammeService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ProgrammeRepository(session)
        self._cat_repo = CategoryRepository(session)

    async def create_category(self, data: ProgrammeCategoryCreate) -> ProgrammeCategory:
        category = ProgrammeCategory(name=data.name, slug=data.get_slug(), description=data.description)
        async with atomic(self._repo._session):
            await self._cat_repo.save(category)
        return category

    async def list_categories(self) -> list[ProgrammeCategory]:
        return await self._cat_repo.list_all()

    async def create_programme(self, data: ProgrammeCreate) -> Programme:
        slug = data.get_slug()
        if await self._repo.get_by_slug(slug):
            raise ConflictError(f"A programme with the name '{data.name}' already exists.")
        programme = Programme(
            slug=slug,
            **{k: v for k, v in data.model_dump().items() if k != "name"},
            name=data.name,
        )
        async with atomic(self._repo._session):
            await self._repo.save(programme)
        return programme

    async def get_programme(self, programme_id: uuid.UUID) -> Programme:
        p = await self._repo.get_by_id(programme_id)
        if p is None:
            raise NotFoundError("Programme not found.")
        return p

    async def list_programmes(
        self,
        limit: int,
        offset: int,
        is_active: bool | None = None,
        is_public: bool | None = None,
        category_id: uuid.UUID | None = None,
    ):
        return await self._repo.list_programmes(limit, offset, is_active, is_public, category_id)

    async def update_programme(self, programme_id: uuid.UUID, data: ProgrammeUpdate) -> Programme:
        p = await self._repo.get_by_id(programme_id)
        if p is None:
            raise NotFoundError("Programme not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(p, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(p)
        return p

    async def create_cohort(self, programme_id: uuid.UUID, data: CohortCreate) -> ProgrammeCohort:
        p = await self._repo.get_by_id(programme_id)
        if p is None:
            raise NotFoundError("Programme not found.")
        cohort = ProgrammeCohort(programme_id=programme_id, **data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save_cohort(cohort)
        return cohort

    async def list_cohorts(self, programme_id: uuid.UUID) -> list[ProgrammeCohort]:
        return await self._repo.list_cohorts(programme_id)
