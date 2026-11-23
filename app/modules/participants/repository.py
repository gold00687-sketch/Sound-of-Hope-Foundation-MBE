import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.participants.models import Participant


class ParticipantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, participant_id: uuid.UUID) -> Participant | None:
        result = await self._session.execute(
            select(Participant).where(Participant.id == participant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Participant | None:
        result = await self._session.execute(
            select(Participant).where(Participant.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        limit: int,
        offset: int,
        query: str | None = None,
        status: str | None = None,
        is_minor: bool | None = None,
    ) -> tuple[list[Participant], int]:
        q = select(Participant)
        count_q = select(func.count()).select_from(Participant)

        filters = []
        if query:
            pattern = f"%{query}%"
            filters.append(
                or_(
                    Participant.first_name.ilike(pattern),
                    Participant.last_name.ilike(pattern),
                    Participant.email.ilike(pattern),
                    Participant.phone.ilike(pattern),
                )
            )
        if status:
            filters.append(Participant.status == status)
        if is_minor is not None:
            filters.append(Participant.is_minor == is_minor)

        for f in filters:
            q = q.where(f)
            count_q = count_q.where(f)

        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Participant.last_name, Participant.first_name).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, participant: Participant) -> Participant:
        self._session.add(participant)
        await self._session.flush()
        return participant
