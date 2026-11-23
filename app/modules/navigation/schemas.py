import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class MenuCreate(BaseModel):
    name: str = Field(max_length=100)
    location: str = Field(max_length=100)


class MenuItemCreate(BaseModel):
    label: str = Field(max_length=200)
    url: str | None = Field(default=None, max_length=500)
    page_id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None
    order: int = 0
    target: str = "_self"


class MenuResponse(BaseModel):
    id: uuid.UUID
    name: str
    location: str
    created_at: datetime
    model_config = {"from_attributes": True}


class MenuItemResponse(BaseModel):
    id: uuid.UUID
    menu_id: uuid.UUID
    label: str
    url: str | None
    page_id: uuid.UUID | None
    parent_id: uuid.UUID | None
    order: int
    target: str
    model_config = {"from_attributes": True}
