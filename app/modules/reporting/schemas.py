import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    report_type: str = Field(max_length=100)
    title: str = Field(max_length=255)
    parameters: dict | None = None


class ReportResponse(BaseModel):
    id: uuid.UUID
    report_type: str
    title: str
    status: str
    file_key: str | None
    completed_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}
