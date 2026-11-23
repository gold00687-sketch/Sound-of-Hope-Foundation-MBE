import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.programmes.schemas import (
    CohortCreate,
    CohortResponse,
    ProgrammeCategoryCreate,
    ProgrammeCategoryResponse,
    ProgrammeCreate,
    ProgrammeResponse,
    ProgrammeUpdate,
)
from app.modules.programmes.service import ProgrammeService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get("/categories", response_model=list[ProgrammeCategoryResponse])
async def list_categories(session: SessionDep):
    return await ProgrammeService(session).list_categories()


@router.post(
    "/categories",
    response_model=ProgrammeCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.PROGRAMME_MANAGE)],
)
async def create_category(body: ProgrammeCategoryCreate, session: SessionDep):
    return await ProgrammeService(session).create_category(body)


@router.get("", response_model=Page[ProgrammeResponse])
async def list_programmes(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    is_active: bool | None = Query(default=None),
    is_public: bool | None = Query(default=None),
    category_id: uuid.UUID | None = Query(default=None),
):
    svc = ProgrammeService(session)
    items, total = await svc.list_programmes(
        pagination.limit, pagination.offset, is_active, is_public, category_id
    )
    return Page.create(items, pagination, total)


@router.post(
    "",
    response_model=ProgrammeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.PROGRAMME_CREATE)],
)
async def create_programme(body: ProgrammeCreate, session: SessionDep):
    return await ProgrammeService(session).create_programme(body)


@router.get("/{programme_id}", response_model=ProgrammeResponse)
async def get_programme(programme_id: uuid.UUID, session: SessionDep):
    return await ProgrammeService(session).get_programme(programme_id)


@router.patch(
    "/{programme_id}",
    response_model=ProgrammeResponse,
    dependencies=[require_permission(Permission.PROGRAMME_UPDATE)],
)
async def update_programme(programme_id: uuid.UUID, body: ProgrammeUpdate, session: SessionDep):
    return await ProgrammeService(session).update_programme(programme_id, body)


@router.get("/{programme_id}/cohorts", response_model=list[CohortResponse])
async def list_cohorts(programme_id: uuid.UUID, session: SessionDep):
    return await ProgrammeService(session).list_cohorts(programme_id)


@router.post(
    "/{programme_id}/cohorts",
    response_model=CohortResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.PROGRAMME_MANAGE)],
)
async def create_cohort(programme_id: uuid.UUID, body: CohortCreate, session: SessionDep):
    return await ProgrammeService(session).create_cohort(programme_id, body)
