import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    title: str = Field(max_length=255)
    body: str
    channel: str = "in_app"
    action_url: str | None = Field(default=None, max_length=500)
    related_type: str | None = Field(default=None, max_length=100)
    related_id: str | None = Field(default=None, max_length=100)


class NotificationResponse(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    channel: str
    is_read: bool
    read_at: datetime | None
    action_url: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
