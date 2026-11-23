import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.guardians.models import Guardian
from app.modules.guardians.repository import GuardianRepository
from app.modules.guardians.schemas import GuardianCreate, GuardianUpdate
from app.modules.participants.models import ParticipantGuardian
from app.modules.participants.repository import ParticipantRepository


class GuardianService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = GuardianRepository(session)
        self._participant_repo = ParticipantRepository(session)

    async def create(self, data: GuardianCreate) -> Guardian:
        guardian = Guardian(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(guardian)
        return guardian

    async def get(self, guardian_id: uuid.UUID) -> Guardian:
        g = await self._repo.get_by_id(guardian_id)
        if g is None:
            raise NotFoundError("Guardian not found.")
        return g

    async def list_guardians(self, limit: int, offset: int):
        return await self._repo.list_all(limit, offset)

    async def update(self, guardian_id: uuid.UUID, data: GuardianUpdate) -> Guardian:
        g = await self._repo.get_by_id(guardian_id)
        if g is None:
            raise NotFoundError("Guardian not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(g, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(g)
        return g

    async def link_to_participant(
        self,
        participant_id: uuid.UUID,
        guardian_id: uuid.UUID,
        relationship_type: str,
        is_primary: bool,
    ) -> None:
        participant = await self._participant_repo.get_by_id(participant_id)
        if participant is None:
            raise NotFoundError("Participant not found.")
        guardian = await self._repo.get_by_id(guardian_id)
        if guardian is None:
            raise NotFoundError("Guardian not found.")
        link = ParticipantGuardian(
            participant_id=participant_id,
            guardian_id=guardian_id,
            relationship_type=relationship_type,
            is_primary=is_primary,
        )
        async with atomic(self._repo._session):
            self._repo._session.add(link)
            await self._repo._session.flush()
