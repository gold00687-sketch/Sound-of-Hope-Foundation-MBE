import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.publications.schemas import (
    PublicationCreate,
    PublicationResponse,
    PublicationUpdate,
)
from app.modules.publications.service import PublicationService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.post(
    "",
    response_model=PublicationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.PUBLICATION_MANAGE)],
)
async def create_publication(
    body: PublicationCreate, session: SessionDep, current_user: CurrentUser
):
    return await PublicationService(session).create(body, current_user.id)


@router.get(
    "",
    response_model=Page[PublicationResponse],
    dependencies=[require_permission(Permission.PUBLICATION_READ)],
)
async def list_publications(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    publication_type: str | None = Query(default=None),
    is_published: bool | None = Query(default=None),
    is_public: bool | None = Query(default=None),
):
    items, total = await PublicationService(session).list_publications(
        pagination.limit, pagination.offset, publication_type, is_published, is_public
    )
    return Page.create(items, pagination, total)


@router.get(
    "/{publication_id}",
    response_model=PublicationResponse,
    dependencies=[require_permission(Permission.PUBLICATION_READ)],
)
async def get_publication(publication_id: uuid.UUID, session: SessionDep):
    return await PublicationService(session).get(publication_id)


@router.patch(
    "/{publication_id}",
    response_model=PublicationResponse,
    dependencies=[require_permission(Permission.CONTENT_MANAGE)],
)
async def update_publication(
    publication_id: uuid.UUID, body: PublicationUpdate, session: SessionDep
):
    return await PublicationService(session).update(publication_id, body)


@router.post(
    "/{publication_id}/publish",
    response_model=PublicationResponse,
    dependencies=[require_permission(Permission.CONTENT_PUBLISH)],
)
async def publish_publication(publication_id: uuid.UUID, session: SessionDep):
    return await PublicationService(session).publish(publication_id)


@router.delete(
    "/{publication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission(Permission.CONTENT_MANAGE)],
)
async def delete_publication(publication_id: uuid.UUID, session: SessionDep):
    await PublicationService(session).delete(publication_id)
