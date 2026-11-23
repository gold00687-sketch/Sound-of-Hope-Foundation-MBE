import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance.models import AttendanceRecord


class AttendanceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_session_and_participant(
        self, session_id: uuid.UUID, participant_id: uuid.UUID
    ) -> AttendanceRecord | None:
        result = await self._session.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.participant_id == participant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_session(self, session_id: uuid.UUID) -> list[AttendanceRecord]:
        result = await self._session.execute(
            select(AttendanceRecord).where(AttendanceRecord.session_id == session_id)
        )
        return list(result.scalars().all())

    async def list_for_participant(
        self, participant_id: uuid.UUID, limit: int, offset: int
    ) -> list[AttendanceRecord]:
        result = await self._session.execute(
            select(AttendanceRecord)
            .where(AttendanceRecord.participant_id == participant_id)
            .order_by(AttendanceRecord.created_at.desc())
            .limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def bulk_save(self, records: list[AttendanceRecord]) -> None:
        for r in records:
            self._session.add(r)
        await self._session.flush()
