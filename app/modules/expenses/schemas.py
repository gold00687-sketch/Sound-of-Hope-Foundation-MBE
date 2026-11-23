import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    programme_id: uuid.UUID | None = None
    category: str = Field(max_length=100)
    description: str
    amount: float = Field(gt=0)
    currency: str = Field(default="UGX", max_length=3)
    expense_date: date


class ExpenseDecision(BaseModel):
    approved: bool
    rejection_reason: str | None = None


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    submitted_by_id: uuid.UUID
    approved_by_id: uuid.UUID | None
    programme_id: uuid.UUID | None
    category: str
    description: str
    amount: float
    currency: str
    expense_date: date
    status: str
    receipt_key: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
