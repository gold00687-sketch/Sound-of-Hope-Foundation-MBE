import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cms.models import Page, PageVersion


class CMSRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------ pages

    async def get_page_by_id(self, page_id: uuid.UUID) -> Page | None:
        result = await self._session.execute(select(Page).where(Page.id == page_id))
        return result.scalar_one_or_none()

    async def get_page_by_slug(self, slug: str) -> Page | None:
        result = await self._session.execute(select(Page).where(Page.slug == slug))
        return result.scalar_one_or_none()

    async def list_pages(
        self,
        limit: int,
        offset: int,
        status: str | None = None,
        q: str | None = None,
    ) -> tuple[list[Page], int]:
        query = select(Page)
        count_q = select(func.count()).select_from(Page)

        if status:
            query = query.where(Page.status == status)
            count_q = count_q.where(Page.status == status)

        if q:
            search = f"%{q}%"
            condition = or_(Page.title.ilike(search), Page.slug.ilike(search))
            query = query.where(condition)
            count_q = count_q.where(condition)

        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            query.order_by(Page.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save_page(self, page: Page) -> None:
        self._session.add(page)
        await self._session.flush()

    async def delete_page(self, page: Page) -> None:
        await self._session.delete(page)
        await self._session.flush()

    # --------------------------------------------------------------- versions

    async def get_version_by_id(self, version_id: uuid.UUID) -> PageVersion | None:
        result = await self._session.execute(
            select(PageVersion).where(PageVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def list_versions(self, page_id: uuid.UUID) -> list[PageVersion]:
        result = await self._session.execute(
            select(PageVersion)
            .where(PageVersion.page_id == page_id)
            .order_by(PageVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def next_version_number(self, page_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.coalesce(func.max(PageVersion.version_number), 0))
            .where(PageVersion.page_id == page_id)
        )
        return result.scalar_one() + 1

    async def save_version(self, version: PageVersion) -> None:
        self._session.add(version)
        await self._session.flush()
