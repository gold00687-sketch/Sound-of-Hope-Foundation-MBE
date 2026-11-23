import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class StaffCreate(BaseModel):
    user_id: uuid.UUID
    department_id: uuid.UUID | None = None
    employee_number: str | None = Field(default=None, max_length=50)
    job_title: str = Field(max_length=200)
    employment_type: Literal["full_time", "part_time", "contract", "volunteer"] = "full_time"
    start_date: date
    notes: str | None = None


class StaffUpdate(BaseModel):
    department_id: uuid.UUID | None = None
    job_title: str | None = Field(default=None, max_length=200)
    employment_type: str | None = None
    end_date: date | None = None
    is_active: bool | None = None
    notes: str | None = None


class StaffResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    department_id: uuid.UUID | None
    employee_number: str | None
    job_title: str
    employment_type: str
    start_date: date
    end_date: date | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
