import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.donations.models import Donation
from app.modules.donations.repository import DonationRepository
from app.modules.donations.schemas import DonationCreate
from app.modules.finance.models import FinancialTransaction
from app.modules.finance.repository import FinanceRepository
from app.utils.helpers import generate_token


class DonationService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = DonationRepository(session)
        self._finance_repo = FinanceRepository(session)

    async def record(self, data: DonationCreate, recorded_by_id: uuid.UUID) -> Donation:
        async with atomic(self._repo._session):
            tx = FinancialTransaction(
                transaction_type="donation",
                amount=data.amount,
                currency=data.currency,
                reference=f"DON-{generate_token(8).upper()}",
                description=f"Donation from {data.donor_name}",
                recorded_by_id=recorded_by_id,
            )
            await self._finance_repo.save(tx)
            donation = Donation(**data.model_dump(), transaction_id=tx.id)
            await self._repo.save(donation)
        return donation

    async def get(self, donation_id: uuid.UUID) -> Donation:
        d = await self._repo.get_by_id(donation_id)
        if d is None:
            raise NotFoundError("Donation not found.")
        return d

    async def list_donations(self, limit: int, offset: int, programme_id: uuid.UUID | None):
        return await self._repo.list_donations(limit, offset, programme_id)
