import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    participant_id: uuid.UUID
    assigned_to_id: uuid.UUID | None = None
    case_type: str = Field(max_length=100)
    summary: str
    is_confidential: bool = True


class CaseUpdate(BaseModel):
    assigned_to_id: uuid.UUID | None = None
    summary: str | None = None
    status: str | None = None


class CaseClose(BaseModel):
    closure_notes: str


class CaseResponse(BaseModel):
    id: uuid.UUID
    participant_id: uuid.UUID
    assigned_to_id: uuid.UUID | None
    case_type: str
    summary: str
    status: str
    is_confidential: bool
    closed_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}
