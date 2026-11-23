import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    participant_id: uuid.UUID | None = None
    programme_id: uuid.UUID | None = None
    idempotency_key: str = Field(max_length=255)
    amount: float = Field(gt=0)
    currency: str = Field(default="UGX", max_length=3)
    payment_method: str = Field(max_length=50)
    description: str | None = None


class PaymentConfirm(BaseModel):
    provider_reference: str = Field(max_length=255)


class PaymentResponse(BaseModel):
    id: uuid.UUID
    participant_id: uuid.UUID | None
    programme_id: uuid.UUID | None
    idempotency_key: str
    amount: float
    currency: str
    payment_method: str
    status: str
    provider_reference: str | None
    paid_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}
