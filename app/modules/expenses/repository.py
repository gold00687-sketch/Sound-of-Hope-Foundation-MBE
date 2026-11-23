import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.expenses.models import Expense


class ExpenseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, expense_id: uuid.UUID) -> Expense | None:
        result = await self._session.execute(select(Expense).where(Expense.id == expense_id))
        return result.scalar_one_or_none()

    async def list_expenses(
        self, limit: int, offset: int,
        status: str | None = None,
        submitted_by_id: uuid.UUID | None = None,
    ) -> tuple[list[Expense], int]:
        q = select(Expense)
        count_q = select(func.count()).select_from(Expense)
        if status:
            q = q.where(Expense.status == status)
            count_q = count_q.where(Expense.status == status)
        if submitted_by_id:
            q = q.where(Expense.submitted_by_id == submitted_by_id)
            count_q = count_q.where(Expense.submitted_by_id == submitted_by_id)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Expense.expense_date.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, obj: Expense) -> Expense:
        self._session.add(obj)
        await self._session.flush()
        return obj
