import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserAddressCreate(BaseModel):
    line1: str = Field(max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(max_length=100)
    region: str | None = Field(default=None, max_length=100)
    country: str = Field(default="Uganda", max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    is_primary: bool = False


class UserAddressResponse(UserAddressCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    model_config = {"from_attributes": True}


class EmergencyContactCreate(BaseModel):
    name: str = Field(max_length=200)
    relationship: str = Field(max_length=100)
    phone: str = Field(max_length=30)
    email: str | None = None


class EmergencyContactResponse(EmergencyContactCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)
    bio: str | None = None


class UserDetailResponse(BaseModel):
    id: uuid.UUID
    email: str
    is_active: bool
    is_email_verified: bool
    first_name: str
    last_name: str
    display_name: str | None
    bio: str | None
    avatar_key: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class AdminUserListItem(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    model_config = {"from_attributes": True}
