import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    transaction_type: str = Field(max_length=50)
    amount: float = Field(gt=0)
    currency: str = Field(default="UGX", max_length=3)
    reference: str = Field(max_length=200)
    description: str | None = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    transaction_type: str
    amount: float
    currency: str
    reference: str
    description: str | None
    occurred_at: datetime
    model_config = {"from_attributes": True}
