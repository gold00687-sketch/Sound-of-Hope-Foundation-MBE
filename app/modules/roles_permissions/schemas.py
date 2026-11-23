import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    name: str = Field(max_length=100)
    display_name: str = Field(max_length=150)
    description: str | None = None


class RoleUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=150)
    description: str | None = None


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    is_system: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class PermissionResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    model_config = {"from_attributes": True}


class AssignPermissionsRequest(BaseModel):
    permission_names: list[str]


class AssignRoleRequest(BaseModel):
    role_name: str


class UserRoleResponse(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID
    role_name: str
    created_at: datetime
    model_config = {"from_attributes": True}
