import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, Field, model_validator


class SessionCreate(BaseModel):
    class_id: uuid.UUID
    lesson_id: uuid.UUID | None = None
    session_date: date
    start_time: time
    end_time: time
    room: str | None = Field(default=None, max_length=100)
    notes: str | None = None

    @model_validator(mode="after")
    def end_after_start(self) -> "SessionCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time.")
        return self


class SessionCancelRequest(BaseModel):
    reason: str | None = None


class SessionResponse(BaseModel):
    id: uuid.UUID
    class_id: uuid.UUID
    lesson_id: uuid.UUID | None
    session_date: date
    start_time: time
    end_time: time
    room: str | None
    is_cancelled: bool
    cancellation_reason: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
