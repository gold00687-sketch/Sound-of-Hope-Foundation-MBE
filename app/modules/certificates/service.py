import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.certificates.models import Certificate
from app.modules.certificates.repository import CertificateRepository
from app.modules.certificates.schemas import CertificateIssue
from app.utils.helpers import generate_token


def _generate_cert_number() -> str:
    import datetime
    year = datetime.date.today().year
    suffix = generate_token(4).upper()
    return f"SOH-{year}-{suffix}"


class CertificateService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CertificateRepository(session)

    async def issue(self, data: CertificateIssue, issued_by_id: uuid.UUID) -> Certificate:
        cert = Certificate(
            **data.model_dump(),
            issued_by_id=issued_by_id,
            certificate_number=_generate_cert_number(),
        )
        try:
            async with atomic(self._repo._session):
                await self._repo.save(cert)
        except IntegrityError:
            raise ConflictError("A certificate has already been issued for this participant and programme/course.")
        return cert

    async def get(self, cert_id: uuid.UUID) -> Certificate:
        c = await self._repo.get_by_id(cert_id)
        if c is None:
            raise NotFoundError("Certificate not found.")
        return c

    async def verify(self, certificate_number: str) -> Certificate:
        c = await self._repo.get_by_number(certificate_number)
        if c is None:
            raise NotFoundError("Certificate not found.")
        return c

    async def list_for_participant(self, participant_id: uuid.UUID) -> list[Certificate]:
        return await self._repo.list_for_participant(participant_id)

    async def revoke(self, cert_id: uuid.UUID, reason: str) -> Certificate:
        c = await self._repo.get_by_id(cert_id)
        if c is None:
            raise NotFoundError("Certificate not found.")
        if c.is_revoked:
            raise ValidationError("Certificate is already revoked.")
        c.is_revoked = True
        c.revocation_reason = reason
        async with atomic(self._repo._session):
            await self._repo.save(c)
        return c
