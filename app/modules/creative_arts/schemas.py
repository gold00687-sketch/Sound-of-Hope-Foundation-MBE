import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    name: str = Field(max_length=255)
    activity_type: str = Field(max_length=100)
    description: str | None = None
    programme_id: uuid.UUID | None = None


class ActivityResponse(BaseModel):
    id: uuid.UUID
    name: str
    activity_type: str
    description: str | None
    programme_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
