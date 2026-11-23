import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MediaAssetResponse(BaseModel):
    id: uuid.UUID
    storage_key: str
    original_filename: str
    mime_type: str
    file_size: int
    alt_text: str | None
    folder: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MediaAssetUpdate(BaseModel):
    alt_text: str | None = Field(default=None, max_length=500)
    folder: str | None = Field(default=None, max_length=200)
