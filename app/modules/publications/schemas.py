import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class PublicationCreate(BaseModel):
    title: str = Field(max_length=255)
    publication_type: Literal["article", "report", "newsletter", "policy", "research"] = "article"
    summary: str | None = None
    body: str | None = None
    published_date: date | None = None
    is_public: bool = True


class PublicationUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    body: str | None = None
    published_date: date | None = None
    is_public: bool | None = None


class PublicationResponse(BaseModel):
    id: uuid.UUID
    title: str
    publication_type: str
    summary: str | None
    published_date: date | None
    is_published: bool
    is_public: bool
    file_key: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
