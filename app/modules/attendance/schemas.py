import uuid
from datetime import datetime

from pydantic import BaseModel

from app.core.constants import AttendanceStatus


class AttendanceEntry(BaseModel):
    participant_id: uuid.UUID
    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: str | None = None


class BulkAttendanceRequest(BaseModel):
    """Record attendance for a whole session in one request."""
    session_id: uuid.UUID
    entries: list[AttendanceEntry]


class AttendanceResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    participant_id: uuid.UUID
    status: str
    notes: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class AttendanceSummary(BaseModel):
    session_id: uuid.UUID
    total: int
    present: int
    absent: int
    late: int
    excused: int
