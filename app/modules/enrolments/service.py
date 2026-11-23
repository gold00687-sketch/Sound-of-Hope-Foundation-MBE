import uuid
from datetime import UTC, date, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import EnrolmentStatus
from app.core.exceptions import ConflictError, DuplicateEnrolmentError, NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.enrolments.models import Enrolment
from app.modules.enrolments.repository import EnrolmentRepository
from app.modules.enrolments.schemas import EnrolmentCreate, EnrolmentUpdate
from app.modules.programmes.repository import ProgrammeRepository


class EnrolmentService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = EnrolmentRepository(session)
        self._programme_repo = ProgrammeRepository(session)

    async def enrol(self, data: EnrolmentCreate, enrolled_by_id: uuid.UUID) -> Enrolment:
        programme = await self._programme_repo.get_by_id(data.programme_id)
        if programme is None:
            raise NotFoundError("Programme not found.")
        if not programme.is_active:
            raise ValidationError("This programme is not currently active.")

        # Check capacity if max_participants is set
        if programme.max_participants is not None:
            _, count = await self._repo.list_for_programme(
                data.programme_id, limit=1, offset=0, status=EnrolmentStatus.ACTIVE
            )
            if count >= programme.max_participants:
                raise ValidationError("This programme has reached its maximum capacity.")

        enrolment = Enrolment(
            programme_id=data.programme_id,
            cohort_id=data.cohort_id,
            participant_id=data.participant_id,
            application_id=data.application_id,
            enrolled_by_id=enrolled_by_id,
            status=EnrolmentStatus.ACTIVE,
            enrolment_date=data.enrolment_date,
            notes=data.notes,
        )
        try:
            async with atomic(self._repo._session):
                await self._repo.save(enrolment)
        except IntegrityError:
            raise DuplicateEnrolmentError()
        return enrolment

    async def get(self, enrolment_id: uuid.UUID) -> Enrolment:
        e = await self._repo.get_by_id(enrolment_id)
        if e is None:
            raise NotFoundError("Enrolment not found.")
        return e

    async def update(self, enrolment_id: uuid.UUID, data: EnrolmentUpdate) -> Enrolment:
        e = await self._repo.get_by_id(enrolment_id)
        if e is None:
            raise NotFoundError("Enrolment not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(e, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(e)
        return e

    async def withdraw(self, enrolment_id: uuid.UUID, reason: str | None = None) -> Enrolment:
        e = await self._repo.get_by_id(enrolment_id)
        if e is None:
            raise NotFoundError("Enrolment not found.")
        if e.status == EnrolmentStatus.WITHDRAWN:
            raise ValidationError("This enrolment has already been withdrawn.")
        e.status = EnrolmentStatus.WITHDRAWN
        e.withdrawal_reason = reason
        async with atomic(self._repo._session):
            await self._repo.save(e)
        return e

    async def list_for_programme(
        self,
        programme_id: uuid.UUID,
        limit: int,
        offset: int,
        status: str | None = None,
        cohort_id: uuid.UUID | None = None,
    ):
        return await self._repo.list_for_programme(programme_id, limit, offset, status, cohort_id)

    async def list_for_participant(self, participant_id: uuid.UUID) -> list[Enrolment]:
        return await self._repo.list_for_participant(participant_id)
