import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ThreadCreate(BaseModel):
    subject: str | None = Field(default=None, max_length=255)
    participant_ids: list[uuid.UUID]


class MessageCreate(BaseModel):
    body: str


class MessageResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    sender_id: uuid.UUID
    body: str
    is_removed: bool
    created_at: datetime
    model_config = {"from_attributes": True}
