import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.media.models import MediaAsset


class MediaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, asset_id: uuid.UUID) -> MediaAsset | None:
        result = await self._session.execute(
            select(MediaAsset).where(MediaAsset.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def list_assets(
        self,
        limit: int,
        offset: int,
        folder: str | None = None,
    ) -> tuple[list[MediaAsset], int]:
        query = select(MediaAsset)
        count_q = select(func.count()).select_from(MediaAsset)

        if folder:
            query = query.where(MediaAsset.folder == folder)
            count_q = count_q.where(MediaAsset.folder == folder)

        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            query.order_by(MediaAsset.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, asset: MediaAsset) -> None:
        self._session.add(asset)
        await self._session.flush()

    async def delete(self, asset: MediaAsset) -> None:
        await self._session.delete(asset)
        await self._session.flush()
