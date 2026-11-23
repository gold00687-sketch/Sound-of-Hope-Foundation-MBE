import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assessments.models import Assessment, AssessmentSubmission


class AssessmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, assessment_id: uuid.UUID) -> Assessment | None:
        result = await self._session.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        return result.scalar_one_or_none()

    async def list_for_course(
        self, course_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Assessment], int]:
        q = select(Assessment).where(Assessment.course_id == course_id)
        count_q = select(func.count()).select_from(Assessment).where(Assessment.course_id == course_id)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(q.order_by(Assessment.due_date.asc().nullslast()).limit(limit).offset(offset))
        return list(result.scalars().all()), total

    async def get_submission(
        self, assessment_id: uuid.UUID, participant_id: uuid.UUID
    ) -> AssessmentSubmission | None:
        result = await self._session.execute(
            select(AssessmentSubmission).where(
                AssessmentSubmission.assessment_id == assessment_id,
                AssessmentSubmission.participant_id == participant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_submissions(self, assessment_id: uuid.UUID) -> list[AssessmentSubmission]:
        result = await self._session.execute(
            select(AssessmentSubmission).where(AssessmentSubmission.assessment_id == assessment_id)
        )
        return list(result.scalars().all())

    async def save(self, obj) -> None:
        self._session.add(obj)
        await self._session.flush()
