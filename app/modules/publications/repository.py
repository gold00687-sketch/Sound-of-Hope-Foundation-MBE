import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.publications.models import Publication


class PublicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, publication_id: uuid.UUID) -> Publication | None:
        result = await self._session.execute(
            select(Publication).where(Publication.id == publication_id)
        )
        return result.scalar_one_or_none()

    async def list_publications(
        self,
        limit: int,
        offset: int,
        publication_type: str | None = None,
        is_published: bool | None = None,
        is_public: bool | None = None,
    ) -> tuple[list[Publication], int]:
        query = select(Publication)
        count_q = select(func.count()).select_from(Publication)

        if publication_type:
            query = query.where(Publication.publication_type == publication_type)
            count_q = count_q.where(Publication.publication_type == publication_type)

        if is_published is not None:
            query = query.where(Publication.is_published == is_published)
            count_q = count_q.where(Publication.is_published == is_published)

        if is_public is not None:
            query = query.where(Publication.is_public == is_public)
            count_q = count_q.where(Publication.is_public == is_public)

        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            query.order_by(Publication.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, publication: Publication) -> None:
        self._session.add(publication)
        await self._session.flush()

    async def delete(self, publication: Publication) -> None:
        await self._session.delete(publication)
        await self._session.flush()
