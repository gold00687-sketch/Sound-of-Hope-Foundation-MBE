import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class VocationalCourseCreate(BaseModel):
    name: str = Field(max_length=255)
    trade: str = Field(max_length=100)
    description: str | None = None
    programme_id: uuid.UUID | None = None


class VocationalCourseResponse(BaseModel):
    id: uuid.UUID
    name: str
    trade: str
    description: str | None
    programme_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
