import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.publications.models import Publication
from app.modules.publications.repository import PublicationRepository
from app.modules.publications.schemas import PublicationCreate, PublicationUpdate


class PublicationService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = PublicationRepository(session)
        self._session = session

    async def create(
        self,
        data: PublicationCreate,
        author_id: uuid.UUID,
    ) -> Publication:
        publication = Publication(
            author_id=author_id,
            title=data.title,
            publication_type=data.publication_type,
            summary=data.summary,
            body=data.body,
            published_date=data.published_date,
            is_public=data.is_public,
            is_published=False,
        )
        async with atomic(self._session):
            await self._repo.save(publication)
        return publication

    async def get(self, publication_id: uuid.UUID) -> Publication:
        pub = await self._repo.get_by_id(publication_id)
        if pub is None:
            raise NotFoundError("Publication not found.")
        return pub

    async def list_publications(
        self,
        limit: int,
        offset: int,
        publication_type: str | None = None,
        is_published: bool | None = None,
        is_public: bool | None = None,
    ) -> tuple[list[Publication], int]:
        return await self._repo.list_publications(
            limit=limit,
            offset=offset,
            publication_type=publication_type,
            is_published=is_published,
            is_public=is_public,
        )

    async def update(
        self,
        publication_id: uuid.UUID,
        data: PublicationUpdate,
    ) -> Publication:
        pub = await self._repo.get_by_id(publication_id)
        if pub is None:
            raise NotFoundError("Publication not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(pub, field, value)
        async with atomic(self._session):
            await self._repo.save(pub)
        return pub

    async def publish(self, publication_id: uuid.UUID) -> Publication:
        pub = await self._repo.get_by_id(publication_id)
        if pub is None:
            raise NotFoundError("Publication not found.")
        if pub.is_published:
            raise ValidationError("Publication is already published.")
        pub.is_published = True
        pub.published_date = pub.published_date or date.today()
        async with atomic(self._session):
            await self._repo.save(pub)
        return pub

    async def delete(self, publication_id: uuid.UUID) -> None:
        pub = await self._repo.get_by_id(publication_id)
        if pub is None:
            raise NotFoundError("Publication not found.")
        async with atomic(self._session):
            await self._repo.delete(pub)
