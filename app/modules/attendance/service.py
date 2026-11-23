import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AttendanceStatus
from app.core.exceptions import ConflictError
from app.infrastructure.database.transaction import atomic
from app.modules.attendance.models import AttendanceRecord
from app.modules.attendance.repository import AttendanceRepository
from app.modules.attendance.schemas import AttendanceSummary, BulkAttendanceRequest


class AttendanceService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AttendanceRepository(session)

    async def record_bulk(
        self, data: BulkAttendanceRequest, recorded_by_id: uuid.UUID
    ) -> list[AttendanceRecord]:
        records = [
            AttendanceRecord(
                session_id=data.session_id,
                participant_id=entry.participant_id,
                status=entry.status,
                notes=entry.notes,
                recorded_by_id=recorded_by_id,
            )
            for entry in data.entries
        ]
        try:
            async with atomic(self._repo._session):
                await self._repo.bulk_save(records)
        except IntegrityError:
            raise ConflictError("Attendance has already been recorded for one or more participants in this session.")
        return records

    async def get_session_attendance(self, session_id: uuid.UUID) -> list[AttendanceRecord]:
        return await self._repo.list_for_session(session_id)

    async def get_participant_attendance(
        self, participant_id: uuid.UUID, limit: int, offset: int
    ) -> list[AttendanceRecord]:
        return await self._repo.list_for_participant(participant_id, limit, offset)

    async def get_session_summary(self, session_id: uuid.UUID) -> AttendanceSummary:
        records = await self._repo.list_for_session(session_id)
        counts: dict[str, int] = {s: 0 for s in AttendanceStatus}
        for r in records:
            counts[r.status] = counts.get(r.status, 0) + 1
        return AttendanceSummary(
            session_id=session_id,
            total=len(records),
            present=counts.get(AttendanceStatus.PRESENT, 0),
            absent=counts.get(AttendanceStatus.ABSENT, 0),
            late=counts.get(AttendanceStatus.LATE, 0),
            excused=counts.get(AttendanceStatus.EXCUSED, 0),
        )
