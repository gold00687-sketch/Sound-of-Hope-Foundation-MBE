import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.safeguarding.schemas import CaseClose, CaseCreate, CaseResponse, CaseUpdate
from app.modules.safeguarding.service import SafeguardingService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()

# Every endpoint requires SAFEGUARDING_READ at minimum.
# Ordinary staff, instructors and programme managers must NOT hold this permission.


@router.get("", response_model=Page[CaseResponse],
            dependencies=[require_permission(Permission.SAFEGUARDING_READ)])
async def list_cases(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    status_filter: str | None = Query(default=None, alias="status"),
):
    items, total = await SafeguardingService(session).list_cases(
        pagination.limit, pagination.offset, status_filter
    )
    return Page.create(items, pagination, total)


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.SAFEGUARDING_MANAGE)])
async def open_case(body: CaseCreate, session: SessionDep, current_user: CurrentUser):
    return await SafeguardingService(session).open_case(body, current_user.id)


@router.get("/{case_id}", response_model=CaseResponse,
            dependencies=[require_permission(Permission.SAFEGUARDING_READ)])
async def get_case(case_id: uuid.UUID, session: SessionDep):
    return await SafeguardingService(session).get(case_id)


@router.patch("/{case_id}", response_model=CaseResponse,
              dependencies=[require_permission(Permission.SAFEGUARDING_MANAGE)])
async def update_case(case_id: uuid.UUID, body: CaseUpdate, session: SessionDep):
    return await SafeguardingService(session).update(case_id, body)


@router.post("/{case_id}/close", response_model=CaseResponse,
             dependencies=[require_permission(Permission.SAFEGUARDING_MANAGE)])
async def close_case(case_id: uuid.UUID, body: CaseClose, session: SessionDep):
    return await SafeguardingService(session).close_case(case_id, body)
