import uuid
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.finance.repository import FinanceRepository


class FinanceService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = FinanceRepository(session)

    async def list_transactions(
        self, limit: int, offset: int, transaction_type: str | None = None
    ):
        return await self._repo.list_transactions(limit, offset, transaction_type)

    async def get_transaction(self, tx_id: uuid.UUID):
        from app.core.exceptions import NotFoundError
        tx = await self._repo.get_by_id(tx_id)
        if tx is None:
            raise NotFoundError("Transaction not found.")
        return tx
