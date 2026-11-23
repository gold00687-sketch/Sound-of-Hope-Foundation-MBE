import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.certificates.models import Certificate


class CertificateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, cert_id: uuid.UUID) -> Certificate | None:
        result = await self._session.execute(select(Certificate).where(Certificate.id == cert_id))
        return result.scalar_one_or_none()

    async def get_by_number(self, number: str) -> Certificate | None:
        result = await self._session.execute(
            select(Certificate).where(Certificate.certificate_number == number)
        )
        return result.scalar_one_or_none()

    async def list_for_participant(self, participant_id: uuid.UUID) -> list[Certificate]:
        result = await self._session.execute(
            select(Certificate)
            .where(Certificate.participant_id == participant_id)
            .order_by(Certificate.issued_date.desc())
        )
        return list(result.scalars().all())

    async def save(self, cert: Certificate) -> Certificate:
        self._session.add(cert)
        await self._session.flush()
        return cert
