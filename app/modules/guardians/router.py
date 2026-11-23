import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.guardians.schemas import (
    GuardianCreate,
    GuardianResponse,
    GuardianUpdate,
    LinkGuardianRequest,
)
from app.modules.guardians.service import GuardianService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get(
    "",
    response_model=Page[GuardianResponse],
    dependencies=[require_permission(Permission.PARTICIPANT_READ)],
)
async def list_guardians(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
):
    svc = GuardianService(session)
    items, total = await svc.list_guardians(pagination.limit, pagination.offset)
    return Page.create(items, pagination, total)


@router.post(
    "",
    response_model=GuardianResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.PARTICIPANT_CREATE)],
)
async def create_guardian(body: GuardianCreate, session: SessionDep):
    return await GuardianService(session).create(body)


@router.get(
    "/{guardian_id}",
    response_model=GuardianResponse,
    dependencies=[require_permission(Permission.PARTICIPANT_READ)],
)
async def get_guardian(guardian_id: uuid.UUID, session: SessionDep):
    return await GuardianService(session).get(guardian_id)


@router.patch(
    "/{guardian_id}",
    response_model=GuardianResponse,
    dependencies=[require_permission(Permission.PARTICIPANT_UPDATE)],
)
async def update_guardian(guardian_id: uuid.UUID, body: GuardianUpdate, session: SessionDep):
    return await GuardianService(session).update(guardian_id, body)


@router.post(
    "/{guardian_id}/participants/{participant_id}/link",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission(Permission.PARTICIPANT_UPDATE)],
)
async def link_guardian_to_participant(
    guardian_id: uuid.UUID,
    participant_id: uuid.UUID,
    body: LinkGuardianRequest,
    session: SessionDep,
) -> None:
    await GuardianService(session).link_to_participant(
        participant_id, guardian_id, body.relationship_type, body.is_primary
    )
