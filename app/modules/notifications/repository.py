import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        result = await self._session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: uuid.UUID, limit: int, offset: int, unread_only: bool = False
    ) -> tuple[list[Notification], int]:
        q = select(Notification).where(Notification.user_id == user_id)
        count_q = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        if unread_only:
            q = q.where(Notification.is_read == False)
            count_q = count_q.where(Notification.is_read == False)
        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def mark_all_read(self, user_id: uuid.UUID) -> None:
        from datetime import UTC, datetime
        from sqlalchemy import update
        await self._session.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.now(UTC))
        )
        await self._session.flush()

    async def save(self, obj: Notification) -> Notification:
        self._session.add(obj)
        await self._session.flush()
        return obj
