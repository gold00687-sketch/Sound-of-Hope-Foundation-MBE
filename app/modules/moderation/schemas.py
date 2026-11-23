import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    content_type: str = Field(max_length=100)
    content_id: str = Field(max_length=100)
    reason: str = Field(max_length=255)
    details: str | None = None


class ReportResponse(BaseModel):
    id: uuid.UUID
    content_type: str
    content_id: str
    reason: str
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}
