import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.participants.schemas import ParticipantCreate, ParticipantResponse, ParticipantUpdate
from app.modules.participants.service import ParticipantService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get(
    "",
    response_model=Page[ParticipantResponse],
    dependencies=[require_permission(Permission.PARTICIPANT_READ)],
)
async def list_participants(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    is_minor: bool | None = Query(default=None),
):
    svc = ParticipantService(session)
    items, total = await svc.search(pagination.limit, pagination.offset, q, status, is_minor)
    return Page.create(items, pagination, total)


@router.post(
    "",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.PARTICIPANT_CREATE)],
)
async def create_participant(body: ParticipantCreate, session: SessionDep):
    return await ParticipantService(session).create(body)


@router.get(
    "/{participant_id}",
    response_model=ParticipantResponse,
    dependencies=[require_permission(Permission.PARTICIPANT_READ)],
)
async def get_participant(participant_id: uuid.UUID, session: SessionDep):
    return await ParticipantService(session).get(participant_id)


@router.patch(
    "/{participant_id}",
    response_model=ParticipantResponse,
    dependencies=[require_permission(Permission.PARTICIPANT_UPDATE)],
)
async def update_participant(
    participant_id: uuid.UUID, body: ParticipantUpdate, session: SessionDep
):
    return await ParticipantService(session).update(participant_id, body)
