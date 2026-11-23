import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GuardianCreate(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: str = Field(max_length=30)
    email: str | None = None
    address: str | None = None
    id_type: str | None = Field(default=None, max_length=100)
    id_number: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    user_id: uuid.UUID | None = None


class GuardianUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = None
    address: str | None = None
    is_active: bool | None = None
    notes: str | None = None


class GuardianResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    first_name: str
    last_name: str
    phone: str
    email: str | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class LinkGuardianRequest(BaseModel):
    guardian_id: uuid.UUID
    relationship_type: str = Field(max_length=100)
    is_primary: bool = False
