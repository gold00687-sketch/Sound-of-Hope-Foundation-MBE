import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PublishStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.cms.models import Page, PageVersion
from app.modules.cms.repository import CMSRepository
from app.modules.cms.schemas import PageCreate, PageUpdate, PageVersionCreate


class CMSService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CMSRepository(session)

    # ------------------------------------------------------------------ pages

    async def create_page(self, data: PageCreate, created_by_id: uuid.UUID) -> Page:
        page = Page(
            slug=data.slug,
            title=data.title,
            meta_description=data.meta_description,
            status=PublishStatus.DRAFT,
            created_by_id=created_by_id,
        )
        try:
            async with atomic(self._repo._session):
                await self._repo.save_page(page)
        except IntegrityError:
            raise ConflictError(f"A page with slug '{data.slug}' already exists.")
        return page

    async def get_page(self, page_id: uuid.UUID) -> Page:
        page = await self._repo.get_page_by_id(page_id)
        if page is None:
            raise NotFoundError("Page not found.")
        return page

    async def list_pages(
        self, limit: int, offset: int, status: str | None, q: str | None
    ) -> tuple[list[Page], int]:
        return await self._repo.list_pages(limit, offset, status, q)

    async def update_page(self, page_id: uuid.UUID, data: PageUpdate) -> Page:
        page = await self._repo.get_page_by_id(page_id)
        if page is None:
            raise NotFoundError("Page not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(page, field, value)
        async with atomic(self._repo._session):
            await self._repo.save_page(page)
        return page

    async def publish_page(self, page_id: uuid.UUID) -> Page:
        """Publish from any status — no restriction."""
        page = await self._repo.get_page_by_id(page_id)
        if page is None:
            raise NotFoundError("Page not found.")
        page.status = PublishStatus.PUBLISHED
        page.published_at = datetime.now(timezone.utc)
        async with atomic(self._repo._session):
            await self._repo.save_page(page)
        return page

    async def unpublish_page(self, page_id: uuid.UUID) -> Page:
        """Revert a published page back to draft."""
        page = await self._repo.get_page_by_id(page_id)
        if page is None:
            raise NotFoundError("Page not found.")
        page.status = PublishStatus.DRAFT
        async with atomic(self._repo._session):
            await self._repo.save_page(page)
        return page

    async def schedule_page(self, page_id: uuid.UUID, publish_at: datetime) -> Page:
        """Mark a page as scheduled for future publication."""
        page = await self._repo.get_page_by_id(page_id)
        if page is None:
            raise NotFoundError("Page not found.")
        page.status = PublishStatus.SCHEDULED
        page.published_at = publish_at
        async with atomic(self._repo._session):
            await self._repo.save_page(page)
        return page

    async def archive_page(self, page_id: uuid.UUID) -> Page:
        """Archive from any status — no restriction."""
        page = await self._repo.get_page_by_id(page_id)
        if page is None:
            raise NotFoundError("Page not found.")
        page.status = PublishStatus.ARCHIVED
        async with atomic(self._repo._session):
            await self._repo.save_page(page)
        return page

    # --------------------------------------------------------------- versions

    async def create_version(
        self, page_id: uuid.UUID, data: PageVersionCreate, created_by_id: uuid.UUID
    ) -> PageVersion:
        page = await self._repo.get_page_by_id(page_id)
        if page is None:
            raise NotFoundError("Page not found.")
        version_number = await self._repo.next_version_number(page_id)
        version = PageVersion(
            page_id=page_id,
            version_number=version_number,
            content_blocks=data.content_blocks,
            created_by_id=created_by_id,
        )
        async with atomic(self._repo._session):
            await self._repo.save_version(version)
        return version

    async def list_versions(self, page_id: uuid.UUID) -> list[PageVersion]:
        page = await self._repo.get_page_by_id(page_id)
        if page is None:
            raise NotFoundError("Page not found.")
        return await self._repo.list_versions(page_id)
