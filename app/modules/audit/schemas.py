import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    resource_type: str | None
    resource_id: str | None
    changes: dict[str, Any] | None
    ip_address: str | None
    detail: str | None
    occurred_at: datetime
    model_config = {"from_attributes": True}
