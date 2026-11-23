import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.enrolments.models import Enrolment


class EnrolmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, enrolment_id: uuid.UUID) -> Enrolment | None:
        result = await self._session.execute(
            select(Enrolment).where(Enrolment.id == enrolment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_programme_and_participant(
        self, programme_id: uuid.UUID, participant_id: uuid.UUID
    ) -> Enrolment | None:
        result = await self._session.execute(
            select(Enrolment).where(
                Enrolment.programme_id == programme_id,
                Enrolment.participant_id == participant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_programme(
        self,
        programme_id: uuid.UUID,
        limit: int,
        offset: int,
        status: str | None = None,
        cohort_id: uuid.UUID | None = None,
    ) -> tuple[list[Enrolment], int]:
        q = select(Enrolment).where(Enrolment.programme_id == programme_id)
        count_q = select(func.count()).select_from(Enrolment).where(
            Enrolment.programme_id == programme_id
        )
        if status:
            q = q.where(Enrolment.status == status)
            count_q = count_q.where(Enrolment.status == status)
        if cohort_id:
            q = q.where(Enrolment.cohort_id == cohort_id)
            count_q = count_q.where(Enrolment.cohort_id == cohort_id)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Enrolment.enrolment_date.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def list_for_participant(self, participant_id: uuid.UUID) -> list[Enrolment]:
        result = await self._session.execute(
            select(Enrolment)
            .where(Enrolment.participant_id == participant_id)
            .order_by(Enrolment.enrolment_date.desc())
        )
        return list(result.scalars().all())

    async def save(self, enrolment: Enrolment) -> Enrolment:
        self._session.add(enrolment)
        await self._session.flush()
        return enrolment
