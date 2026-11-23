import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.guardians.models import Guardian


class GuardianRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, guardian_id: uuid.UUID) -> Guardian | None:
        result = await self._session.execute(
            select(Guardian).where(Guardian.id == guardian_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, limit: int, offset: int) -> tuple[list[Guardian], int]:
        from sqlalchemy import func
        count = (await self._session.execute(
            select(func.count()).select_from(Guardian)
        )).scalar_one()
        result = await self._session.execute(
            select(Guardian).order_by(Guardian.last_name).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), count

    async def save(self, guardian: Guardian) -> Guardian:
        self._session.add(guardian)
        await self._session.flush()
        return guardian
