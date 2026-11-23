import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ReferralCreate(BaseModel):
    participant_id: uuid.UUID
    referral_type: str = Field(max_length=100)
    destination: str = Field(max_length=255)
    reason: str
    referred_at: datetime


class ReferralResponse(BaseModel):
    id: uuid.UUID
    participant_id: uuid.UUID
    referral_type: str
    destination: str
    status: str
    referred_at: datetime
    created_at: datetime
    model_config = {"from_attributes": True}
