import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.repository import AuditRepository


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AuditRepository(session)

    async def log(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        changes: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        detail: str | None = None,
    ) -> None:
        await self._repo.record(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            detail=detail,
        )

    async def list_logs(
        self,
        limit: int,
        offset: int,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ):
        return await self._repo.list_logs(
            limit, offset, user_id, action, resource_type, from_date, to_date
        )
