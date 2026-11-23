import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.safeguarding.models import SafeguardingCase


class SafeguardingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, case_id: uuid.UUID) -> SafeguardingCase | None:
        result = await self._session.execute(
            select(SafeguardingCase).where(SafeguardingCase.id == case_id)
        )
        return result.scalar_one_or_none()

    async def list_cases(
        self, limit: int, offset: int, status: str | None = None
    ) -> tuple[list[SafeguardingCase], int]:
        q = select(SafeguardingCase)
        count_q = select(func.count()).select_from(SafeguardingCase)
        if status:
            q = q.where(SafeguardingCase.status == status)
            count_q = count_q.where(SafeguardingCase.status == status)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(SafeguardingCase.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, obj: SafeguardingCase) -> SafeguardingCase:
        self._session.add(obj)
        await self._session.flush()
        return obj
