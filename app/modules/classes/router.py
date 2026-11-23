import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.classes.schemas import ClassCreate, ClassResponse, ClassUpdate
from app.modules.classes.service import ClassService
from app.modules.schedules.schemas import SessionCreate, SessionCancelRequest, SessionResponse
from app.modules.schedules.service import ScheduleService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get("", response_model=Page[ClassResponse], dependencies=[require_permission(Permission.CLASS_READ)])
async def list_classes(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    course_id: uuid.UUID | None = Query(default=None),
    cohort_id: uuid.UUID | None = Query(default=None),
    instructor_id: uuid.UUID | None = Query(default=None),
):
    items, total = await ClassService(session).list_classes(
        pagination.limit, pagination.offset, course_id, cohort_id, instructor_id
    )
    return Page.create(items, pagination, total)


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.CLASS_MANAGE)])
async def create_class(body: ClassCreate, session: SessionDep):
    return await ClassService(session).create(body)


@router.get("/{class_id}", response_model=ClassResponse, dependencies=[require_permission(Permission.CLASS_READ)])
async def get_class(class_id: uuid.UUID, session: SessionDep):
    return await ClassService(session).get(class_id)


@router.patch("/{class_id}", response_model=ClassResponse, dependencies=[require_permission(Permission.CLASS_MANAGE)])
async def update_class(class_id: uuid.UUID, body: ClassUpdate, session: SessionDep):
    return await ClassService(session).update(class_id, body)


@router.get("/{class_id}/sessions", response_model=list[SessionResponse],
            dependencies=[require_permission(Permission.CLASS_READ)])
async def list_sessions(
    class_id: uuid.UUID, session: SessionDep,
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
):
    return await ScheduleService(session).list_for_class(class_id, from_date, to_date)


@router.post("/{class_id}/sessions", response_model=SessionResponse,
             status_code=status.HTTP_201_CREATED, dependencies=[require_permission(Permission.CLASS_MANAGE)])
async def create_session(class_id: uuid.UUID, body: SessionCreate, session: SessionDep):
    body.class_id = class_id
    return await ScheduleService(session).create_session(body)


@router.post("/sessions/{session_id}/cancel", response_model=SessionResponse,
             dependencies=[require_permission(Permission.CLASS_MANAGE)])
async def cancel_session(session_id: uuid.UUID, body: SessionCancelRequest, session: SessionDep):
    return await ScheduleService(session).cancel_session(session_id, body.reason)
