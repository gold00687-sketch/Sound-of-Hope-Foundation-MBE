import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.applications.models import Application


class ApplicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        result = await self._session.execute(
            select(Application).where(Application.id == application_id)
        )
        return result.scalar_one_or_none()

    async def get_by_programme_and_participant(
        self, programme_id: uuid.UUID, participant_id: uuid.UUID
    ) -> Application | None:
        result = await self._session.execute(
            select(Application).where(
                Application.programme_id == programme_id,
                Application.participant_id == participant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_programme(
        self, programme_id: uuid.UUID, limit: int, offset: int, status: str | None = None
    ) -> tuple[list[Application], int]:
        q = select(Application).where(Application.programme_id == programme_id)
        count_q = select(func.count()).select_from(Application).where(
            Application.programme_id == programme_id
        )
        if status:
            q = q.where(Application.status == status)
            count_q = count_q.where(Application.status == status)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Application.submitted_at.desc().nullslast()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, application: Application) -> Application:
        self._session.add(application)
        await self._session.flush()
        return application
