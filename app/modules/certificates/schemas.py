import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class CertificateIssue(BaseModel):
    participant_id: uuid.UUID
    programme_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None
    title: str = Field(max_length=255)
    description: str | None = None
    issued_date: date
    expiry_date: date | None = None


class CertificateResponse(BaseModel):
    id: uuid.UUID
    participant_id: uuid.UUID
    programme_id: uuid.UUID | None
    course_id: uuid.UUID | None
    certificate_number: str
    title: str
    issued_date: date
    expiry_date: date | None
    document_key: str | None
    is_revoked: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class RevokeRequest(BaseModel):
    reason: str
