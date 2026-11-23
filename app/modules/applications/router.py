import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.applications.schemas import (
    ApplicationCreate,
    ApplicationDecision,
    ApplicationResponse,
    ApplicationSubmit,
)
from app.modules.applications.service import ApplicationService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get(
    "",
    response_model=Page[ApplicationResponse],
    dependencies=[require_permission(Permission.APPLICATION_READ)],
)
async def list_applications_for_programme(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    programme_id: uuid.UUID = Query(...),
    status_filter: str | None = Query(default=None, alias="status"),
):
    items, total = await ApplicationService(session).list_for_programme(
        programme_id, pagination.limit, pagination.offset, status_filter
    )
    return Page.create(items, pagination, total)


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.APPLICATION_READ)],
)
async def create_application(body: ApplicationCreate, session: SessionDep):
    return await ApplicationService(session).create(body)


@router.post(
    "/{application_id}/submit",
    response_model=ApplicationResponse,
    dependencies=[require_permission(Permission.APPLICATION_READ)],
)
async def submit_application(
    application_id: uuid.UUID, body: ApplicationSubmit, session: SessionDep
):
    return await ApplicationService(session).submit(application_id, body)


@router.post(
    "/{application_id}/review",
    response_model=ApplicationResponse,
    dependencies=[require_permission(Permission.APPLICATION_REVIEW)],
)
async def review_application(
    application_id: uuid.UUID,
    body: ApplicationDecision,
    session: SessionDep,
    current_user: CurrentUser,
):
    return await ApplicationService(session).review(application_id, body, current_user.id)


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    dependencies=[require_permission(Permission.APPLICATION_READ)],
)
async def get_application(application_id: uuid.UUID, session: SessionDep):
    return await ApplicationService(session).get(application_id)
