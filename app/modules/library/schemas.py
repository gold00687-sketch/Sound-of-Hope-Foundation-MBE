import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ResourceCreate(BaseModel):
    title: str = Field(max_length=255)
    resource_type: str = Field(max_length=100)
    description: str | None = None
    author: str | None = Field(default=None, max_length=255)
    external_url: str | None = Field(default=None, max_length=500)
    is_public: bool = True


class ResourceResponse(BaseModel):
    id: uuid.UUID
    title: str
    resource_type: str
    description: str | None
    author: str | None
    file_key: str | None
    external_url: str | None
    is_public: bool
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
