import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.expenses.models import Expense
from app.modules.expenses.repository import ExpenseRepository
from app.modules.expenses.schemas import ExpenseCreate, ExpenseDecision
from app.modules.finance.models import FinancialTransaction
from app.modules.finance.repository import FinanceRepository
from app.utils.helpers import generate_token


class ExpenseService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ExpenseRepository(session)
        self._finance_repo = FinanceRepository(session)

    async def submit(self, data: ExpenseCreate, submitted_by_id: uuid.UUID) -> Expense:
        expense = Expense(**data.model_dump(), submitted_by_id=submitted_by_id)
        async with atomic(self._repo._session):
            await self._repo.save(expense)
        return expense

    async def get(self, expense_id: uuid.UUID) -> Expense:
        e = await self._repo.get_by_id(expense_id)
        if e is None:
            raise NotFoundError("Expense not found.")
        return e

    async def list_expenses(
        self, limit: int, offset: int, status: str | None, submitted_by_id: uuid.UUID | None
    ):
        return await self._repo.list_expenses(limit, offset, status, submitted_by_id)

    async def decide(
        self, expense_id: uuid.UUID, data: ExpenseDecision, decided_by_id: uuid.UUID
    ) -> Expense:
        expense = await self._repo.get_by_id(expense_id)
        if expense is None:
            raise NotFoundError("Expense not found.")
        if expense.status != "pending":
            raise ValidationError("Only pending expenses can be approved or rejected.")

        async with atomic(self._repo._session):
            if data.approved:
                tx = FinancialTransaction(
                    transaction_type="expense",
                    amount=float(expense.amount),
                    currency=expense.currency,
                    reference=f"EXP-{generate_token(8).upper()}",
                    description=expense.description,
                    recorded_by_id=decided_by_id,
                )
                await self._finance_repo.save(tx)
                expense.transaction_id = tx.id
                expense.status = "approved"
            else:
                expense.status = "rejected"
                expense.rejection_reason = data.rejection_reason
            expense.approved_by_id = decided_by_id
            await self._repo.save(expense)
        return expense
