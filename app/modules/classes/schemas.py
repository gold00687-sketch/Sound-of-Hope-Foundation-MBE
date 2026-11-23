import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class ClassCreate(BaseModel):
    course_id: uuid.UUID
    cohort_id: uuid.UUID | None = None
    instructor_id: uuid.UUID | None = None
    name: str = Field(max_length=255)
    room: str | None = Field(default=None, max_length=100)
    max_capacity: int | None = Field(default=None, ge=1)
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class ClassUpdate(BaseModel):
    instructor_id: uuid.UUID | None = None
    name: str | None = Field(default=None, max_length=255)
    room: str | None = Field(default=None, max_length=100)
    max_capacity: int | None = Field(default=None, ge=1)
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
    notes: str | None = None


class ClassResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    cohort_id: uuid.UUID | None
    instructor_id: uuid.UUID | None
    name: str
    room: str | None
    max_capacity: int | None
    start_date: date | None
    end_date: date | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
