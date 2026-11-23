import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.enrolments.schemas import EnrolmentCreate, EnrolmentResponse, EnrolmentUpdate
from app.modules.enrolments.service import EnrolmentService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


class WithdrawRequest(BaseModel):
    reason: str | None = None


@router.post(
    "",
    response_model=EnrolmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.ENROLMENT_CREATE)],
)
async def enrol_participant(
    body: EnrolmentCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    return await EnrolmentService(session).enrol(body, current_user.id)


@router.get(
    "/{enrolment_id}",
    response_model=EnrolmentResponse,
    dependencies=[require_permission(Permission.ENROLMENT_READ)],
)
async def get_enrolment(enrolment_id: uuid.UUID, session: SessionDep):
    return await EnrolmentService(session).get(enrolment_id)


@router.patch(
    "/{enrolment_id}",
    response_model=EnrolmentResponse,
    dependencies=[require_permission(Permission.ENROLMENT_UPDATE)],
)
async def update_enrolment(
    enrolment_id: uuid.UUID, body: EnrolmentUpdate, session: SessionDep
):
    return await EnrolmentService(session).update(enrolment_id, body)


@router.post(
    "/{enrolment_id}/withdraw",
    response_model=EnrolmentResponse,
    dependencies=[require_permission(Permission.ENROLMENT_UPDATE)],
)
async def withdraw_enrolment(
    enrolment_id: uuid.UUID, body: WithdrawRequest, session: SessionDep
):
    return await EnrolmentService(session).withdraw(enrolment_id, body.reason)


@router.get(
    "/participant/{participant_id}",
    response_model=list[EnrolmentResponse],
    dependencies=[require_permission(Permission.ENROLMENT_READ)],
)
async def participant_enrolments(participant_id: uuid.UUID, session: SessionDep):
    return await EnrolmentService(session).list_for_participant(participant_id)
