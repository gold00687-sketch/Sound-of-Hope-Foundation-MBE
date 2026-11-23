import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class DiscussionCreate(BaseModel):
    title: str = Field(max_length=255)
    body: str
    context_type: str | None = Field(default=None, max_length=100)
    context_id: str | None = Field(default=None, max_length=100)


class DiscussionResponse(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    context_type: str | None
    context_id: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    body: str


class CommentResponse(BaseModel):
    id: uuid.UUID
    discussion_id: uuid.UUID
    body: str
    is_removed: bool
    created_at: datetime
    model_config = {"from_attributes": True}
