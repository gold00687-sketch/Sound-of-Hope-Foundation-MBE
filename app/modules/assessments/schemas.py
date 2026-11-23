import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    course_id: uuid.UUID
    class_id: uuid.UUID | None = None
    title: str = Field(max_length=255)
    description: str | None = None
    assessment_type: Literal["assignment", "quiz", "exam", "practical", "project"] = "assignment"
    max_score: float = Field(default=100.0, gt=0)
    passing_score: float | None = Field(default=None, gt=0)
    due_date: date | None = None


class AssessmentResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    class_id: uuid.UUID | None
    title: str
    assessment_type: str
    max_score: float
    passing_score: float | None
    due_date: date | None
    is_published: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class SubmissionCreate(BaseModel):
    participant_id: uuid.UUID
    submitted_at: datetime | None = None


class GradeSubmission(BaseModel):
    score: float = Field(ge=0)
    feedback: str | None = None


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    assessment_id: uuid.UUID
    participant_id: uuid.UUID
    score: float | None
    feedback: str | None
    submitted_at: datetime | None
    graded_at: datetime | None
    is_passed: bool | None
    created_at: datetime
    model_config = {"from_attributes": True}
