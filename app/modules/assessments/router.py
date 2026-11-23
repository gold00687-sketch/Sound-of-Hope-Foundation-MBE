import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.assessments.schemas import (
    AssessmentCreate, AssessmentResponse,
    GradeSubmission, SubmissionCreate, SubmissionResponse,
)
from app.modules.assessments.service import AssessmentService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.ASSESSMENT_MANAGE)])
async def create_assessment(body: AssessmentCreate, session: SessionDep):
    return await AssessmentService(session).create(body)


@router.get("/{assessment_id}", response_model=AssessmentResponse,
            dependencies=[require_permission(Permission.ASSESSMENT_READ)])
async def get_assessment(assessment_id: uuid.UUID, session: SessionDep):
    return await AssessmentService(session).get(assessment_id)


@router.post("/{assessment_id}/publish", response_model=AssessmentResponse,
             dependencies=[require_permission(Permission.ASSESSMENT_MANAGE)])
async def publish_assessment(assessment_id: uuid.UUID, session: SessionDep):
    return await AssessmentService(session).publish(assessment_id)


@router.post("/{assessment_id}/submissions", response_model=SubmissionResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.ASSESSMENT_READ)])
async def submit(assessment_id: uuid.UUID, body: SubmissionCreate, session: SessionDep):
    return await AssessmentService(session).submit(assessment_id, body)


@router.get("/{assessment_id}/submissions", response_model=list[SubmissionResponse],
            dependencies=[require_permission(Permission.ASSESSMENT_READ)])
async def list_submissions(assessment_id: uuid.UUID, session: SessionDep):
    return await AssessmentService(session).list_submissions(assessment_id)


@router.post("/{assessment_id}/submissions/{participant_id}/grade",
             response_model=SubmissionResponse,
             dependencies=[require_permission(Permission.ASSESSMENT_MANAGE)])
async def grade_submission(
    assessment_id: uuid.UUID,
    participant_id: uuid.UUID,
    body: GradeSubmission,
    session: SessionDep,
    current_user: CurrentUser,
):
    return await AssessmentService(session).grade(
        assessment_id, participant_id, body, current_user.id
    )
