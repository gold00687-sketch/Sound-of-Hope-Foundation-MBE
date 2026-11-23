import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.core.constants import EnrolmentStatus


class EnrolmentCreate(BaseModel):
    programme_id: uuid.UUID
    participant_id: uuid.UUID
    cohort_id: uuid.UUID | None = None
    application_id: uuid.UUID | None = None
    enrolment_date: date
    notes: str | None = None


class EnrolmentUpdate(BaseModel):
    cohort_id: uuid.UUID | None = None
    status: EnrolmentStatus | None = None
    completion_date: date | None = None
    withdrawal_reason: str | None = None
    notes: str | None = None


class EnrolmentResponse(BaseModel):
    id: uuid.UUID
    programme_id: uuid.UUID
    cohort_id: uuid.UUID | None
    participant_id: uuid.UUID
    application_id: uuid.UUID | None
    status: str
    enrolment_date: date
    completion_date: date | None
    notes: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
