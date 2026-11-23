import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class InstrumentCreate(BaseModel):
    name: str = Field(max_length=200)
    category: str = Field(max_length=100)
    serial_number: str | None = Field(default=None, max_length=100)
    condition: str = "good"
    notes: str | None = None


class InstrumentResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    serial_number: str | None
    condition: str
    is_available: bool
    created_at: datetime
    model_config = {"from_attributes": True}
