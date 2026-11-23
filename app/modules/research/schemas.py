import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field


class ResearchProjectCreate(BaseModel):
    title: str = Field(max_length=255)
    abstract: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ResearchProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    abstract: str | None
    status: str
    is_published: bool
    created_at: datetime
    model_config = {"from_attributes": True}
