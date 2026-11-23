import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.finance.models import FinancialTransaction


class FinanceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, tx_id: uuid.UUID) -> FinancialTransaction | None:
        result = await self._session.execute(
            select(FinancialTransaction).where(FinancialTransaction.id == tx_id)
        )
        return result.scalar_one_or_none()

    async def list_transactions(
        self, limit: int, offset: int, transaction_type: str | None = None
    ) -> tuple[list[FinancialTransaction], int]:
        q = select(FinancialTransaction)
        count_q = select(func.count()).select_from(FinancialTransaction)
        if transaction_type:
            q = q.where(FinancialTransaction.transaction_type == transaction_type)
            count_q = count_q.where(FinancialTransaction.transaction_type == transaction_type)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(FinancialTransaction.occurred_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, obj: FinancialTransaction) -> FinancialTransaction:
        self._session.add(obj)
        await self._session.flush()
        return obj
