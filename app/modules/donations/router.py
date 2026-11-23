import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.donations.schemas import DonationCreate, DonationResponse
from app.modules.donations.service import DonationService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.post("", response_model=DonationResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.DONATION_MANAGE)])
async def record_donation(body: DonationCreate, session: SessionDep, current_user: CurrentUser):
    return await DonationService(session).record(body, current_user.id)


@router.get("", response_model=Page[DonationResponse],
            dependencies=[require_permission(Permission.DONATION_READ)])
async def list_donations(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    programme_id: uuid.UUID | None = Query(default=None),
):
    items, total = await DonationService(session).list_donations(
        pagination.limit, pagination.offset, programme_id
    )
    return Page.create(items, pagination, total)


@router.get("/{donation_id}", response_model=DonationResponse,
            dependencies=[require_permission(Permission.DONATION_READ)])
async def get_donation(donation_id: uuid.UUID, session: SessionDep):
    return await DonationService(session).get(donation_id)
