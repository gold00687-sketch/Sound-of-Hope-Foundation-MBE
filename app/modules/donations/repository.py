import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.donations.models import Donation


class DonationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, donation_id: uuid.UUID) -> Donation | None:
        result = await self._session.execute(select(Donation).where(Donation.id == donation_id))
        return result.scalar_one_or_none()

    async def list_donations(
        self, limit: int, offset: int, programme_id: uuid.UUID | None = None
    ) -> tuple[list[Donation], int]:
        q = select(Donation)
        count_q = select(func.count()).select_from(Donation)
        if programme_id:
            q = q.where(Donation.programme_id == programme_id)
            count_q = count_q.where(Donation.programme_id == programme_id)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Donation.received_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, obj: Donation) -> Donation:
        self._session.add(obj)
        await self._session.flush()
        return obj
