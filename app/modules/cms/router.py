import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.cms.schemas import (
    PageCreate,
    PageResponse,
    PageUpdate,
    PageVersionCreate,
    PageVersionResponse,
)
from app.modules.cms.service import CMSService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.post(
    "/pages",
    response_model=PageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.CONTENT_CREATE)],
)
async def create_page(body: PageCreate, session: SessionDep, current_user: CurrentUser):
    return await CMSService(session).create_page(body, current_user.id)


@router.get("/pages", response_model=Page[PageResponse])
async def list_pages(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
):
    """
    List CMS pages. No authentication required — the public frontend
    uses this to fetch published pages by slug.
    Authenticated back-office requests can see all statuses.
    """
    items, total = await CMSService(session).list_pages(
        pagination.limit, pagination.offset, status_filter, q
    )
    return Page.create(items, pagination, total)


@router.get(
    "/pages/{page_id}",
    response_model=PageResponse,
)
async def get_page(page_id: uuid.UUID, session: SessionDep):
    """Get a single CMS page by ID. Public — no auth required."""
    return await CMSService(session).get_page(page_id)


@router.patch(
    "/pages/{page_id}",
    response_model=PageResponse,
    dependencies=[require_permission(Permission.CONTENT_MANAGE)],
)
async def update_page(page_id: uuid.UUID, body: PageUpdate, session: SessionDep):
    return await CMSService(session).update_page(page_id, body)


@router.post(
    "/pages/{page_id}/versions",
    response_model=PageVersionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.CONTENT_MANAGE)],
)
async def create_page_version(
    page_id: uuid.UUID,
    body: PageVersionCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    return await CMSService(session).create_version(page_id, body, current_user.id)


@router.get(
    "/pages/{page_id}/versions",
    response_model=list[PageVersionResponse],
)
async def list_page_versions(page_id: uuid.UUID, session: SessionDep):
    """List versions for a page. Public — the frontend reads this to render content."""
    return await CMSService(session).list_versions(page_id)


@router.post(
    "/pages/{page_id}/publish",
    response_model=PageResponse,
    dependencies=[require_permission(Permission.CONTENT_PUBLISH)],
)
async def publish_page(page_id: uuid.UUID, session: SessionDep):
    """Publish a page from any status."""
    return await CMSService(session).publish_page(page_id)


@router.post(
    "/pages/{page_id}/unpublish",
    response_model=PageResponse,
    dependencies=[require_permission(Permission.CONTENT_MANAGE)],
)
async def unpublish_page(page_id: uuid.UUID, session: SessionDep):
    """Revert a published page back to draft."""
    return await CMSService(session).unpublish_page(page_id)


@router.post(
    "/pages/{page_id}/schedule",
    response_model=PageResponse,
    dependencies=[require_permission(Permission.CONTENT_PUBLISH)],
)
async def schedule_page(
    page_id: uuid.UUID,
    session: SessionDep,
    publish_at: datetime = Query(..., description="ISO-8601 datetime to publish at"),
):
    """Schedule a page for future publication."""
    return await CMSService(session).schedule_page(page_id, publish_at)


@router.post(
    "/pages/{page_id}/archive",
    response_model=PageResponse,
    dependencies=[require_permission(Permission.CONTENT_MANAGE)],
)
async def archive_page(page_id: uuid.UUID, session: SessionDep):
    """Archive a page from any status."""
    return await CMSService(session).archive_page(page_id)
