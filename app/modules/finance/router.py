import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.finance.schemas import TransactionResponse
from app.modules.finance.service import FinanceService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get("", response_model=Page[TransactionResponse],
            dependencies=[require_permission(Permission.FINANCE_READ)])
async def list_transactions(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    transaction_type: str | None = Query(default=None),
):
    items, total = await FinanceService(session).list_transactions(
        pagination.limit, pagination.offset, transaction_type
    )
    return Page.create(items, pagination, total)


@router.get("/{tx_id}", response_model=TransactionResponse,
            dependencies=[require_permission(Permission.FINANCE_READ)])
async def get_transaction(tx_id: uuid.UUID, session: SessionDep):
    return await FinanceService(session).get_transaction(tx_id)
