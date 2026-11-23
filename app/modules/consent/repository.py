import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.consent.models import ConsentRecord


class ConsentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, consent_id: uuid.UUID) -> ConsentRecord | None:
        result = await self._session.execute(
            select(ConsentRecord).where(ConsentRecord.id == consent_id)
        )
        return result.scalar_one_or_none()

    async def list_for_participant(self, participant_id: uuid.UUID) -> list[ConsentRecord]:
        result = await self._session.execute(
            select(ConsentRecord)
            .where(ConsentRecord.participant_id == participant_id)
            .order_by(ConsentRecord.given_at.desc())
        )
        return list(result.scalars().all())

    async def save(self, obj: ConsentRecord) -> ConsentRecord:
        self._session.add(obj)
        await self._session.flush()
        return obj
