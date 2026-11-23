import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.payments.schemas import PaymentConfirm, PaymentCreate, PaymentResponse
from app.modules.payments.service import PaymentService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.PAYMENT_MANAGE)])
async def initiate_payment(body: PaymentCreate, session: SessionDep, current_user: CurrentUser):
    return await PaymentService(session).initiate(body, current_user.id)


@router.post("/{payment_id}/confirm", response_model=PaymentResponse,
             dependencies=[require_permission(Permission.PAYMENT_MANAGE)])
async def confirm_payment(
    payment_id: uuid.UUID, body: PaymentConfirm, session: SessionDep, current_user: CurrentUser
):
    return await PaymentService(session).confirm(payment_id, body, current_user.id)


@router.get("/{payment_id}", response_model=PaymentResponse,
            dependencies=[require_permission(Permission.PAYMENT_READ)])
async def get_payment(payment_id: uuid.UUID, session: SessionDep):
    return await PaymentService(session).get(payment_id)


@router.get("", response_model=Page[PaymentResponse],
            dependencies=[require_permission(Permission.PAYMENT_READ)])
async def list_payments(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    participant_id: uuid.UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
):
    items, total = await PaymentService(session).list_payments(
        pagination.limit, pagination.offset, participant_id, status_filter
    )
    return Page.create(items, pagination, total)
