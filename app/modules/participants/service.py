import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.participants.models import Participant
from app.modules.participants.repository import ParticipantRepository
from app.modules.participants.schemas import ParticipantCreate, ParticipantUpdate


class ParticipantService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ParticipantRepository(session)

    async def create(self, data: ParticipantCreate) -> Participant:
        participant = Participant(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(participant)
        return participant

    async def get(self, participant_id: uuid.UUID) -> Participant:
        p = await self._repo.get_by_id(participant_id)
        if p is None:
            raise NotFoundError("Participant not found.")
        return p

    async def search(self, limit: int, offset: int, query: str | None, status: str | None, is_minor: bool | None):
        return await self._repo.search(limit, offset, query, status, is_minor)

    async def update(self, participant_id: uuid.UUID, data: ParticipantUpdate) -> Participant:
        p = await self._repo.get_by_id(participant_id)
        if p is None:
            raise NotFoundError("Participant not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(p, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(p)
        return p
