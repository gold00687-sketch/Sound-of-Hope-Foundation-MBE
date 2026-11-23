import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.consent.models import ConsentRecord
from app.modules.consent.repository import ConsentRepository
from app.modules.consent.schemas import ConsentCreate, ConsentWithdraw


class ConsentService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ConsentRepository(session)

    async def record(self, data: ConsentCreate) -> ConsentRecord:
        consent = ConsentRecord(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(consent)
        return consent

    async def get(self, consent_id: uuid.UUID) -> ConsentRecord:
        c = await self._repo.get_by_id(consent_id)
        if c is None:
            raise NotFoundError("Consent record not found.")
        return c

    async def list_for_participant(self, participant_id: uuid.UUID) -> list[ConsentRecord]:
        return await self._repo.list_for_participant(participant_id)

    async def withdraw(self, consent_id: uuid.UUID, data: ConsentWithdraw) -> ConsentRecord:
        c = await self._repo.get_by_id(consent_id)
        if c is None:
            raise NotFoundError("Consent record not found.")
        if not c.is_active:
            raise ValidationError("Consent is already withdrawn.")
        c.is_active = False
        c.withdrawn_at = datetime.now(UTC)
        c.withdrawal_reason = data.reason
        async with atomic(self._repo._session):
            await self._repo.save(c)
        return c
