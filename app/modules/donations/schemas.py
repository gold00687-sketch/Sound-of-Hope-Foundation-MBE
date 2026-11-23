import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DonationCreate(BaseModel):
    donor_name: str = Field(max_length=255)
    donor_email: str | None = Field(default=None, max_length=255)
    donor_phone: str | None = Field(default=None, max_length=30)
    amount: float = Field(gt=0)
    currency: str = Field(default="UGX", max_length=3)
    payment_method: str = Field(max_length=50)
    programme_id: uuid.UUID | None = None
    is_anonymous: bool = False
    notes: str | None = None
    received_at: datetime


class DonationResponse(BaseModel):
    id: uuid.UUID
    donor_name: str
    donor_email: str | None
    amount: float
    currency: str
    payment_method: str
    programme_id: uuid.UUID | None
    is_anonymous: bool
    received_at: datetime
    created_at: datetime
    model_config = {"from_attributes": True}
