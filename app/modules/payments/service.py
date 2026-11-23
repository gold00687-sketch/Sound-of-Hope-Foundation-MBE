import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.finance.models import FinancialTransaction
from app.modules.finance.repository import FinanceRepository
from app.modules.payments.models import Payment
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import PaymentConfirm, PaymentCreate
from app.utils.helpers import generate_token


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = PaymentRepository(session)
        self._finance_repo = FinanceRepository(session)

    async def initiate(self, data: PaymentCreate, recorded_by_id: uuid.UUID) -> Payment:
        # Idempotency: return existing record for the same key
        existing = await self._repo.get_by_idempotency_key(data.idempotency_key)
        if existing:
            return existing

        payment = Payment(**data.model_dump(), status="pending")
        try:
            async with atomic(self._repo._session):
                await self._repo.save(payment)
        except IntegrityError:
            raise ConflictError("Duplicate payment key.")
        return payment

    async def confirm(
        self, payment_id: uuid.UUID, data: PaymentConfirm, recorded_by_id: uuid.UUID
    ) -> Payment:
        payment = await self._repo.get_by_id(payment_id)
        if payment is None:
            raise NotFoundError("Payment not found.")

        async with atomic(self._repo._session):
            tx = FinancialTransaction(
                transaction_type="payment",
                amount=float(payment.amount),
                currency=payment.currency,
                reference=f"PAY-{generate_token(8).upper()}",
                description=payment.description,
                recorded_by_id=recorded_by_id,
            )
            await self._finance_repo.save(tx)
            payment.status = "completed"
            payment.provider_reference = data.provider_reference
            payment.paid_at = datetime.now(UTC)
            payment.transaction_id = tx.id
            await self._repo.save(payment)
        return payment

    async def get(self, payment_id: uuid.UUID) -> Payment:
        p = await self._repo.get_by_id(payment_id)
        if p is None:
            raise NotFoundError("Payment not found.")
        return p

    async def list_payments(
        self, limit: int, offset: int,
        participant_id: uuid.UUID | None,
        status: str | None,
    ):
        return await self._repo.list_payments(limit, offset, participant_id, status)
