import uuid
from datetime import datetime

from pydantic import BaseModel

from app.core.constants import ApplicationStatus


class ApplicationCreate(BaseModel):
    programme_id: uuid.UUID
    participant_id: uuid.UUID
    motivation: str | None = None


class ApplicationSubmit(BaseModel):
    motivation: str | None = None


class ApplicationDecision(BaseModel):
    status: ApplicationStatus
    review_notes: str | None = None


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    programme_id: uuid.UUID
    participant_id: uuid.UUID
    status: str
    motivation: str | None
    submitted_at: datetime | None
    reviewed_at: datetime | None
    review_notes: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
