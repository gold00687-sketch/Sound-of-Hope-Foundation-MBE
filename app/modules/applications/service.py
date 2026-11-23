import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ApplicationStatus
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.applications.models import Application
from app.modules.applications.repository import ApplicationRepository
from app.modules.applications.schemas import ApplicationCreate, ApplicationDecision, ApplicationSubmit
from app.modules.programmes.repository import ProgrammeRepository


class ApplicationService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ApplicationRepository(session)
        self._programme_repo = ProgrammeRepository(session)

    async def create(self, data: ApplicationCreate) -> Application:
        programme = await self._programme_repo.get_by_id(data.programme_id)
        if programme is None:
            raise NotFoundError("Programme not found.")
        if not programme.is_active:
            raise ValidationError("This programme is not currently accepting applications.")
        existing = await self._repo.get_by_programme_and_participant(
            data.programme_id, data.participant_id
        )
        if existing:
            raise ConflictError("An application for this participant already exists.")
        application = Application(
            programme_id=data.programme_id,
            participant_id=data.participant_id,
            motivation=data.motivation,
            status=ApplicationStatus.DRAFT,
        )
        async with atomic(self._repo._session):
            await self._repo.save(application)
        return application

    async def submit(self, application_id: uuid.UUID, data: ApplicationSubmit) -> Application:
        app = await self._repo.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        if app.status != ApplicationStatus.DRAFT:
            raise ValidationError("Only draft applications can be submitted.")
        app.status = ApplicationStatus.SUBMITTED
        app.submitted_at = datetime.now(UTC)
        if data.motivation:
            app.motivation = data.motivation
        async with atomic(self._repo._session):
            await self._repo.save(app)
        return app

    async def review(
        self,
        application_id: uuid.UUID,
        data: ApplicationDecision,
        reviewer_id: uuid.UUID,
    ) -> Application:
        app = await self._repo.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        if app.status not in (ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW, ApplicationStatus.WAITLISTED):
            raise ValidationError("This application cannot be reviewed in its current state.")
        app.status = data.status
        app.review_notes = data.review_notes
        app.reviewed_by_id = reviewer_id
        app.reviewed_at = datetime.now(UTC)
        async with atomic(self._repo._session):
            await self._repo.save(app)
        return app

    async def get(self, application_id: uuid.UUID) -> Application:
        app = await self._repo.get_by_id(application_id)
        if app is None:
            raise NotFoundError("Application not found.")
        return app

    async def list_for_programme(
        self, programme_id: uuid.UUID, limit: int, offset: int, status: str | None
    ):
        return await self._repo.list_for_programme(programme_id, limit, offset, status)
