import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    status: str
    start_date: date | None
    end_date: date | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
