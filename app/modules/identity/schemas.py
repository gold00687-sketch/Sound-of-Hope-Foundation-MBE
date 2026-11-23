import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.validators import normalise_email, normalise_phone


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("email", mode="before")
    @classmethod
    def normalise_email_field(cls, v: str) -> str:
        return normalise_email(v)

    @field_validator("phone", mode="before")
    @classmethod
    def normalise_phone_field(cls, v: str | None) -> str | None:
        if v is None:
            return None
        from app.utils.validators import is_valid_phone

        normalised = normalise_phone(v)
        if not is_valid_phone(normalised):
            raise ValueError("Invalid phone number format.")
        return normalised

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalise(cls, v: str) -> str:
        return normalise_email(v)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def complexity(cls, v: str) -> str:
        return RegisterRequest.password_complexity(v)


class PasswordResetRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalise(cls, v: str) -> str:
        return normalise_email(v)


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def complexity(cls, v: str) -> str:
        return RegisterRequest.password_complexity(v)


class EmailVerifyRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    is_active: bool
    is_email_verified: bool
    first_name: str
    last_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    display_name: str
    description: str | None

    model_config = {"from_attributes": True}


class AssignRoleRequest(BaseModel):
    user_id: uuid.UUID
    role_name: str
