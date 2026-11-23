import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class BookingCreate(BaseModel):
    act_id: str = Field(max_length=100)
    act_name: str = Field(max_length=255)
    booker_name: str = Field(max_length=255)
    booker_email: EmailStr
    booker_phone: str | None = Field(default=None, max_length=50)
    event_type: str = Field(max_length=100)
    event_date: date
    event_location: str = Field(max_length=255)
    guest_count: int | None = Field(default=None, ge=1)
    duration_hours: float | None = Field(default=None, gt=0)
    notes: str | None = None
    fee_amount: float = Field(gt=0)
    fee_currency: str = Field(default="USD", max_length=3)


class BookingStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|confirmed|cancelled)$")
    internal_notes: str | None = None


class BookingResponse(BaseModel):
    id: uuid.UUID
    act_id: str
    act_name: str
    booker_name: str
    booker_email: str
    booker_phone: str | None
    event_type: str
    event_date: date
    event_location: str
    guest_count: int | None
    duration_hours: float | None
    notes: str | None
    fee_amount: float
    fee_currency: str
    status: str
    confirmed_at: datetime | None
    cancelled_at: datetime | None
    internal_notes: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
