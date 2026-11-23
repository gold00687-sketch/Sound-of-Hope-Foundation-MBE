import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.safeguarding.models import SafeguardingCase
from app.modules.safeguarding.repository import SafeguardingRepository
from app.modules.safeguarding.schemas import CaseClose, CaseCreate, CaseUpdate


class SafeguardingService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = SafeguardingRepository(session)

    async def open_case(self, data: CaseCreate, opened_by_id: uuid.UUID) -> SafeguardingCase:
        case = SafeguardingCase(**data.model_dump(), opened_by_id=opened_by_id)
        async with atomic(self._repo._session):
            await self._repo.save(case)
        return case

    async def get(self, case_id: uuid.UUID) -> SafeguardingCase:
        c = await self._repo.get_by_id(case_id)
        if c is None:
            raise NotFoundError("Case not found.")
        return c

    async def list_cases(self, limit: int, offset: int, status: str | None):
        return await self._repo.list_cases(limit, offset, status)

    async def update(self, case_id: uuid.UUID, data: CaseUpdate) -> SafeguardingCase:
        c = await self._repo.get_by_id(case_id)
        if c is None:
            raise NotFoundError("Case not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(c, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(c)
        return c

    async def close_case(self, case_id: uuid.UUID, data: CaseClose) -> SafeguardingCase:
        c = await self._repo.get_by_id(case_id)
        if c is None:
            raise NotFoundError("Case not found.")
        c.status = "closed"
        c.closed_at = datetime.now(UTC)
        c.closure_notes = data.closure_notes
        async with atomic(self._repo._session):
            await self._repo.save(c)
        return c
