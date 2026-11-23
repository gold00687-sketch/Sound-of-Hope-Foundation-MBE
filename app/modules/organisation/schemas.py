import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class OrganisationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    tagline: str | None = Field(default=None, max_length=300)
    description: str | None = None
    mission: str | None = None
    vision: str | None = None
    website: str | None = Field(default=None, max_length=300)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)


class OrganisationResponse(BaseModel):
    id: uuid.UUID
    name: str
    legal_name: str | None
    tagline: str | None
    description: str | None
    mission: str | None
    vision: str | None
    website: str | None
    email: str | None
    phone: str | None
    city: str | None
    country: str
    logo_key: str | None
    model_config = {"from_attributes": True}


class DepartmentCreate(BaseModel):
    name: str = Field(max_length=200)
    code: str | None = Field(default=None, max_length=50)
    description: str | None = None
    parent_id: uuid.UUID | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    parent_id: uuid.UUID | None = None
    is_active: bool | None = None


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str | None
    description: str | None
    parent_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
