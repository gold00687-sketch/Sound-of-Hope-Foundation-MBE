import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ConsentCreate(BaseModel):
    participant_id: uuid.UUID
    guardian_id: uuid.UUID | None = None
    consent_type: str = Field(max_length=100)
    purpose: str
    given_at: datetime
    expires_at: datetime | None = None


class ConsentWithdraw(BaseModel):
    reason: str | None = None


class ConsentResponse(BaseModel):
    id: uuid.UUID
    participant_id: uuid.UUID
    guardian_id: uuid.UUID | None
    consent_type: str
    purpose: str
    given_at: datetime
    expires_at: datetime | None
    is_active: bool
    withdrawn_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}
