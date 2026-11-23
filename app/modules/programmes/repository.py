import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.programmes.models import Programme, ProgrammeCategory, ProgrammeCohort


class ProgrammeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, programme_id: uuid.UUID) -> Programme | None:
        result = await self._session.execute(
            select(Programme).where(Programme.id == programme_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Programme | None:
        result = await self._session.execute(
            select(Programme).where(Programme.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_programmes(
        self,
        limit: int,
        offset: int,
        is_active: bool | None = None,
        is_public: bool | None = None,
        category_id: uuid.UUID | None = None,
    ) -> tuple[list[Programme], int]:
        q = select(Programme)
        count_q = select(func.count()).select_from(Programme)

        if is_active is not None:
            q = q.where(Programme.is_active == is_active)
            count_q = count_q.where(Programme.is_active == is_active)
        if is_public is not None:
            q = q.where(Programme.is_public == is_public)
            count_q = count_q.where(Programme.is_public == is_public)
        if category_id is not None:
            q = q.where(Programme.category_id == category_id)
            count_q = count_q.where(Programme.category_id == category_id)

        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Programme.name).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, programme: Programme) -> Programme:
        self._session.add(programme)
        await self._session.flush()
        return programme

    async def get_cohort(self, cohort_id: uuid.UUID) -> ProgrammeCohort | None:
        result = await self._session.execute(
            select(ProgrammeCohort).where(ProgrammeCohort.id == cohort_id)
        )
        return result.scalar_one_or_none()

    async def list_cohorts(self, programme_id: uuid.UUID) -> list[ProgrammeCohort]:
        result = await self._session.execute(
            select(ProgrammeCohort)
            .where(ProgrammeCohort.programme_id == programme_id)
            .order_by(ProgrammeCohort.start_date)
        )
        return list(result.scalars().all())

    async def save_cohort(self, cohort: ProgrammeCohort) -> ProgrammeCohort:
        self._session.add(cohort)
        await self._session.flush()
        return cohort


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, category_id: uuid.UUID) -> ProgrammeCategory | None:
        result = await self._session.execute(
            select(ProgrammeCategory).where(ProgrammeCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ProgrammeCategory]:
        result = await self._session.execute(
            select(ProgrammeCategory)
            .where(ProgrammeCategory.is_active == True)
            .order_by(ProgrammeCategory.name)
        )
        return list(result.scalars().all())

    async def save(self, category: ProgrammeCategory) -> ProgrammeCategory:
        self._session.add(category)
        await self._session.flush()
        return category
