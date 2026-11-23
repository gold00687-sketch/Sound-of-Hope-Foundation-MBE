import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class EventCreate(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = None
    event_type: Literal["general", "workshop", "concert", "exhibition", "community", "training"] = "general"
    location: str | None = Field(default=None, max_length=300)
    is_online: bool = False
    online_link: str | None = Field(default=None, max_length=500)
    starts_at: datetime
    ends_at: datetime
    max_attendees: int | None = Field(default=None, ge=1)
    is_public: bool = True

    @model_validator(mode="after")
    def end_after_start(self) -> "EventCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at.")
        return self


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    location: str | None = Field(default=None, max_length=300)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    max_attendees: int | None = Field(default=None, ge=1)
    is_public: bool | None = None


class EventResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    event_type: str
    location: str | None
    is_online: bool
    starts_at: datetime
    ends_at: datetime
    max_attendees: int | None
    is_public: bool
    is_published: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class RegistrationCreate(BaseModel):
    participant_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    notes: str | None = None


class RegistrationResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    participant_id: uuid.UUID | None
    user_id: uuid.UUID | None
    status: str
    attended: bool
    created_at: datetime
    model_config = {"from_attributes": True}
