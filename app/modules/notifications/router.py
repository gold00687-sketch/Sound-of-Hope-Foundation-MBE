import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.modules.identity.dependencies import CurrentUser
from app.modules.notifications.schemas import NotificationResponse
from app.modules.notifications.service import NotificationService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get("", response_model=Page[NotificationResponse])
async def my_notifications(
    session: SessionDep,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    unread_only: bool = Query(default=False),
):
    items, total = await NotificationService(session).list_for_user(
        current_user.id, pagination.limit, pagination.offset, unread_only
    )
    return Page.create(items, pagination, total)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
):
    return await NotificationService(session).mark_read(notification_id, current_user.id)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(session: SessionDep, current_user: CurrentUser) -> None:
    await NotificationService(session).mark_all_read(current_user.id)
