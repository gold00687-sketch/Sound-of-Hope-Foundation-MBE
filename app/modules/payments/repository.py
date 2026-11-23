import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        result = await self._session.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, key: str) -> Payment | None:
        result = await self._session.execute(
            select(Payment).where(Payment.idempotency_key == key)
        )
        return result.scalar_one_or_none()

    async def list_payments(
        self, limit: int, offset: int,
        participant_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> tuple[list[Payment], int]:
        q = select(Payment)
        count_q = select(func.count()).select_from(Payment)
        if participant_id:
            q = q.where(Payment.participant_id == participant_id)
            count_q = count_q.where(Payment.participant_id == participant_id)
        if status:
            q = q.where(Payment.status == status)
            count_q = count_q.where(Payment.status == status)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Payment.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, obj: Payment) -> Payment:
        self._session.add(obj)
        await self._session.flush()
        return obj
