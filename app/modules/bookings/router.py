import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.bookings.schemas import BookingCreate, BookingResponse, BookingStatusUpdate
from app.modules.bookings.service import BookingService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a musician booking enquiry (public)",
)
async def create_booking(body: BookingCreate, session: SessionDep):
    """
    Public endpoint — no authentication required.
    Creates a booking record with status 'pending'.
    """
    return await BookingService(session).create(body)


@router.get(
    "",
    response_model=Page[BookingResponse],
    dependencies=[require_permission(Permission.BOOKING_READ)],
    summary="List all bookings (staff)",
)
async def list_bookings(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    act_id: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
):
    items, total = await BookingService(session).list_bookings(
        pagination.limit, pagination.offset, act_id, status_filter
    )
    return Page.create(items, pagination, total)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    dependencies=[require_permission(Permission.BOOKING_READ)],
    summary="Get a single booking (staff)",
)
async def get_booking(booking_id: uuid.UUID, session: SessionDep):
    return await BookingService(session).get(booking_id)


@router.patch(
    "/{booking_id}/status",
    response_model=BookingResponse,
    dependencies=[require_permission(Permission.BOOKING_MANAGE)],
    summary="Update booking status (staff)",
)
async def update_booking_status(
    booking_id: uuid.UUID, body: BookingStatusUpdate, session: SessionDep
):
    return await BookingService(session).update_status(booking_id, body)
