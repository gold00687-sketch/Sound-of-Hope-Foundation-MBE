import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.expenses.schemas import ExpenseCreate, ExpenseDecision, ExpenseResponse
from app.modules.expenses.service import ExpenseService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.EXPENSE_READ)])
async def submit_expense(body: ExpenseCreate, session: SessionDep, current_user: CurrentUser):
    return await ExpenseService(session).submit(body, current_user.id)


@router.get("", response_model=Page[ExpenseResponse],
            dependencies=[require_permission(Permission.EXPENSE_READ)])
async def list_expenses(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    status_filter: str | None = Query(default=None, alias="status"),
    submitted_by_id: uuid.UUID | None = Query(default=None),
):
    items, total = await ExpenseService(session).list_expenses(
        pagination.limit, pagination.offset, status_filter, submitted_by_id
    )
    return Page.create(items, pagination, total)


@router.get("/{expense_id}", response_model=ExpenseResponse,
            dependencies=[require_permission(Permission.EXPENSE_READ)])
async def get_expense(expense_id: uuid.UUID, session: SessionDep):
    return await ExpenseService(session).get(expense_id)


@router.post("/{expense_id}/decide", response_model=ExpenseResponse,
             dependencies=[require_permission(Permission.EXPENSE_MANAGE)])
async def decide_expense(
    expense_id: uuid.UUID, body: ExpenseDecision, session: SessionDep, current_user: CurrentUser
):
    return await ExpenseService(session).decide(expense_id, body, current_user.id)
