import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.events.schemas import (
    EventCreate, EventResponse, EventUpdate,
    RegistrationCreate, RegistrationResponse,
)
from app.modules.events.service import EventService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get("", response_model=Page[EventResponse])
async def list_events(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    is_public: bool | None = Query(default=None),
    from_date: datetime | None = Query(default=None),
):
    items, total = await EventService(session).list_events(
        pagination.limit, pagination.offset, is_public, from_date
    )
    return Page.create(items, pagination, total)


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.EVENT_CREATE)])
async def create_event(body: EventCreate, session: SessionDep, current_user: CurrentUser):
    return await EventService(session).create(body, current_user.id)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: uuid.UUID, session: SessionDep):
    return await EventService(session).get(event_id)


@router.patch("/{event_id}", response_model=EventResponse,
              dependencies=[require_permission(Permission.EVENT_MANAGE)])
async def update_event(event_id: uuid.UUID, body: EventUpdate, session: SessionDep):
    return await EventService(session).update(event_id, body)


@router.post("/{event_id}/publish", response_model=EventResponse,
             dependencies=[require_permission(Permission.EVENT_MANAGE)])
async def publish_event(event_id: uuid.UUID, session: SessionDep):
    return await EventService(session).publish(event_id)


@router.post("/{event_id}/register", response_model=RegistrationResponse,
             status_code=status.HTTP_201_CREATED)
async def register_for_event(event_id: uuid.UUID, body: RegistrationCreate, session: SessionDep):
    return await EventService(session).register(event_id, body)


@router.get("/{event_id}/registrations", response_model=list[RegistrationResponse],
            dependencies=[require_permission(Permission.EVENT_READ)])
async def list_registrations(event_id: uuid.UUID, session: SessionDep):
    return await EventService(session).list_registrations(event_id)
