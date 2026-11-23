import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class InitiativeCreate(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = None
    is_public: bool = True


class InitiativeResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    status: str
    is_public: bool
    created_at: datetime
    model_config = {"from_attributes": True}
