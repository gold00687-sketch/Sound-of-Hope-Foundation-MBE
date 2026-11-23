import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.assessments.models import Assessment, AssessmentSubmission
from app.modules.assessments.repository import AssessmentRepository
from app.modules.assessments.schemas import AssessmentCreate, GradeSubmission, SubmissionCreate


class AssessmentService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AssessmentRepository(session)

    async def create(self, data: AssessmentCreate) -> Assessment:
        assessment = Assessment(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(assessment)
        return assessment

    async def get(self, assessment_id: uuid.UUID) -> Assessment:
        a = await self._repo.get_by_id(assessment_id)
        if a is None:
            raise NotFoundError("Assessment not found.")
        return a

    async def publish(self, assessment_id: uuid.UUID) -> Assessment:
        a = await self._repo.get_by_id(assessment_id)
        if a is None:
            raise NotFoundError("Assessment not found.")
        a.is_published = True
        async with atomic(self._repo._session):
            await self._repo.save(a)
        return a

    async def list_for_course(self, course_id: uuid.UUID, limit: int, offset: int):
        return await self._repo.list_for_course(course_id, limit, offset)

    async def submit(self, assessment_id: uuid.UUID, data: SubmissionCreate) -> AssessmentSubmission:
        a = await self._repo.get_by_id(assessment_id)
        if a is None:
            raise NotFoundError("Assessment not found.")
        submission = AssessmentSubmission(
            assessment_id=assessment_id,
            participant_id=data.participant_id,
            submitted_at=data.submitted_at or datetime.now(UTC),
        )
        try:
            async with atomic(self._repo._session):
                await self._repo.save(submission)
        except IntegrityError:
            raise ConflictError("A submission already exists for this participant.")
        return submission

    async def grade(
        self, assessment_id: uuid.UUID, participant_id: uuid.UUID,
        data: GradeSubmission, graded_by_id: uuid.UUID,
    ) -> AssessmentSubmission:
        a = await self._repo.get_by_id(assessment_id)
        if a is None:
            raise NotFoundError("Assessment not found.")
        if data.score > float(a.max_score):
            raise ValidationError(f"Score cannot exceed maximum of {a.max_score}.")
        submission = await self._repo.get_submission(assessment_id, participant_id)
        if submission is None:
            raise NotFoundError("Submission not found.")
        submission.score = data.score
        submission.feedback = data.feedback
        submission.graded_by_id = graded_by_id
        submission.graded_at = datetime.now(UTC)
        submission.is_passed = (
            data.score >= float(a.passing_score)
            if a.passing_score is not None else None
        )
        async with atomic(self._repo._session):
            await self._repo.save(submission)
        return submission

    async def list_submissions(self, assessment_id: uuid.UUID) -> list[AssessmentSubmission]:
        return await self._repo.list_submissions(assessment_id)
