import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        changes: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        detail: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            detail=detail,
        )
        self._session.add(log)
        await self._session.flush()
        return log

    async def list_logs(
        self,
        limit: int,
        offset: int,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> tuple[list[AuditLog], int]:
        q = select(AuditLog)
        count_q = select(func.count()).select_from(AuditLog)

        filters = []
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if action:
            filters.append(AuditLog.action == action)
        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)
        if from_date:
            filters.append(AuditLog.occurred_at >= from_date)
        if to_date:
            filters.append(AuditLog.occurred_at <= to_date)

        for f in filters:
            q = q.where(f)
            count_q = count_q.where(f)

        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(AuditLog.occurred_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total
