import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import PublishStatus


class PageCreate(BaseModel):
    slug: str = Field(max_length=255)
    title: str = Field(max_length=255)
    meta_description: str | None = Field(default=None, max_length=500)


class PageUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = Field(default=None, max_length=500)


class PageVersionCreate(BaseModel):
    content_blocks: dict[str, Any]


class PageResponse(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    meta_description: str | None
    status: str
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PageVersionResponse(BaseModel):
    id: uuid.UUID
    page_id: uuid.UUID
    version_number: int
    content_blocks: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
