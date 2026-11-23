import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.utils.helpers import slugify


class ProgrammeCategoryCreate(BaseModel):
    name: str = Field(max_length=200)
    description: str | None = None

    def get_slug(self) -> str:
        return slugify(self.name)


class ProgrammeCategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    is_active: bool
    model_config = {"from_attributes": True}


class ProgrammeCreate(BaseModel):
    name: str = Field(max_length=255)
    category_id: uuid.UUID | None = None
    description: str | None = None
    objectives: str | None = None
    target_audience: str | None = None
    max_participants: int | None = Field(default=None, ge=1)
    start_date: date | None = None
    end_date: date | None = None
    requires_application: bool = True
    is_public: bool = True

    def get_slug(self) -> str:
        return slugify(self.name)


class ProgrammeUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    category_id: uuid.UUID | None = None
    description: str | None = None
    objectives: str | None = None
    target_audience: str | None = None
    max_participants: int | None = Field(default=None, ge=1)
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
    requires_application: bool | None = None
    is_public: bool | None = None


class ProgrammeResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category_id: uuid.UUID | None
    description: str | None
    objectives: str | None
    target_audience: str | None
    max_participants: int | None
    start_date: date | None
    end_date: date | None
    is_active: bool
    requires_application: bool
    is_public: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class CohortCreate(BaseModel):
    name: str = Field(max_length=200)
    start_date: date | None = None
    end_date: date | None = None
    max_participants: int | None = Field(default=None, ge=1)


class CohortResponse(BaseModel):
    id: uuid.UUID
    programme_id: uuid.UUID
    name: str
    start_date: date | None
    end_date: date | None
    max_participants: int | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
