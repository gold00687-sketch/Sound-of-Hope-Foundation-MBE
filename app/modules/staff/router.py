import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.staff.schemas import StaffCreate, StaffResponse, StaffUpdate
from app.modules.staff.service import StaffService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get(
    "",
    response_model=Page[StaffResponse],
    dependencies=[require_permission(Permission.STAFF_READ)],
)
async def list_staff(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    department_id: uuid.UUID | None = Query(default=None),
    is_active: bool | None = Query(default=None),
):
    svc = StaffService(session)
    staff, total = await svc.list_staff(
        pagination.limit, pagination.offset, department_id, is_active
    )
    return Page.create(staff, pagination, total)


@router.post(
    "",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.STAFF_CREATE)],
)
async def create_staff(body: StaffCreate, session: SessionDep):
    return await StaffService(session).create(body)


@router.get(
    "/{staff_id}",
    response_model=StaffResponse,
    dependencies=[require_permission(Permission.STAFF_READ)],
)
async def get_staff(staff_id: uuid.UUID, session: SessionDep):
    return await StaffService(session).get(staff_id)


@router.patch(
    "/{staff_id}",
    response_model=StaffResponse,
    dependencies=[require_permission(Permission.STAFF_UPDATE)],
)
async def update_staff(staff_id: uuid.UUID, body: StaffUpdate, session: SessionDep):
    return await StaffService(session).update(staff_id, body)
