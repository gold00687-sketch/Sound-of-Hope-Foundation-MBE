import uuid

from fastapi import APIRouter, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.organisation.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    OrganisationResponse,
    OrganisationUpdate,
)
from app.modules.organisation.service import OrganisationService

router = APIRouter()


def _svc(session: SessionDep) -> OrganisationService:
    return OrganisationService(session)


@router.get("", response_model=OrganisationResponse)
async def get_organisation(session: SessionDep):
    return await _svc(session).get_organisation()


@router.put(
    "",
    response_model=OrganisationResponse,
    dependencies=[require_permission(Permission.ORGANISATION_UPDATE)],
)
async def update_organisation(body: OrganisationUpdate, session: SessionDep):
    return await _svc(session).update_organisation(body)


@router.get("/departments", response_model=list[DepartmentResponse])
async def list_departments(session: SessionDep, include_inactive: bool = False):
    return await _svc(session).list_departments(include_inactive)


@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.ORGANISATION_UPDATE)],
)
async def create_department(body: DepartmentCreate, session: SessionDep):
    return await _svc(session).create_department(body)


@router.patch(
    "/departments/{dept_id}",
    response_model=DepartmentResponse,
    dependencies=[require_permission(Permission.ORGANISATION_UPDATE)],
)
async def update_department(dept_id: uuid.UUID, body: DepartmentUpdate, session: SessionDep):
    return await _svc(session).update_department(dept_id, body)
