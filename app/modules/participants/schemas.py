import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.constants import Gender, ParticipantStatus


class ParticipantCreate(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    date_of_birth: date | None = None
    gender: Gender | None = None
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = None
    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    nationality: str | None = Field(default=None, max_length=100)
    is_minor: bool = False
    notes: str | None = None
    user_id: uuid.UUID | None = None


class ParticipantUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    date_of_birth: date | None = None
    gender: Gender | None = None
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = None
    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    status: ParticipantStatus | None = None
    notes: str | None = None


class ParticipantResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    first_name: str
    last_name: str
    date_of_birth: date | None
    gender: str | None
    phone: str | None
    email: str | None
    city: str | None
    nationality: str | None
    status: str
    is_minor: bool
    created_at: datetime
    model_config = {"from_attributes": True}
