import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.attendance.schemas import (
    AttendanceResponse, AttendanceSummary, BulkAttendanceRequest
)
from app.modules.attendance.service import AttendanceService
from app.utils.pagination import PaginationParams

router = APIRouter()


@router.post("", response_model=list[AttendanceResponse],
             status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.ATTENDANCE_RECORD)])
async def record_attendance(
    body: BulkAttendanceRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    return await AttendanceService(session).record_bulk(body, current_user.id)


@router.get("/session/{session_id}", response_model=list[AttendanceResponse],
            dependencies=[require_permission(Permission.ATTENDANCE_READ)])
async def session_attendance(session_id: uuid.UUID, session: SessionDep):
    return await AttendanceService(session).get_session_attendance(session_id)


@router.get("/session/{session_id}/summary", response_model=AttendanceSummary,
            dependencies=[require_permission(Permission.ATTENDANCE_READ)])
async def session_summary(session_id: uuid.UUID, session: SessionDep):
    return await AttendanceService(session).get_session_summary(session_id)


@router.get("/participant/{participant_id}", response_model=list[AttendanceResponse],
            dependencies=[require_permission(Permission.ATTENDANCE_READ)])
async def participant_attendance(
    participant_id: uuid.UUID,
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
):
    return await AttendanceService(session).get_participant_attendance(
        participant_id, pagination.limit, pagination.offset
    )
