import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    name: str = Field(max_length=255)
    code: str | None = Field(default=None, max_length=50)
    programme_id: uuid.UUID | None = None
    description: str | None = None
    objectives: str | None = None
    duration_weeks: int | None = Field(default=None, ge=1)


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    objectives: str | None = None
    duration_weeks: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class CourseResponse(BaseModel):
    id: uuid.UUID
    programme_id: uuid.UUID | None
    name: str
    code: str | None
    description: str | None
    duration_weeks: int | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class ModuleCreate(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = None
    order: int = Field(default=0, ge=0)


class ModuleResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    name: str
    description: str | None
    order: int
    model_config = {"from_attributes": True}


class LessonCreate(BaseModel):
    title: str = Field(max_length=255)
    content: str | None = None
    duration_minutes: int | None = Field(default=None, ge=1)
    order: int = Field(default=0, ge=0)


class LessonResponse(BaseModel):
    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    content: str | None
    duration_minutes: int | None
    order: int
    is_published: bool
    model_config = {"from_attributes": True}
