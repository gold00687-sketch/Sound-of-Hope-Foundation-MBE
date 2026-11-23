import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.infrastructure.database.transaction import atomic
from app.modules.notifications.models import Notification
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import NotificationCreate


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = NotificationRepository(session)

    async def create(self, data: NotificationCreate) -> Notification:
        notification = Notification(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(notification)
        return notification

    async def list_for_user(
        self, user_id: uuid.UUID, limit: int, offset: int, unread_only: bool = False
    ):
        return await self._repo.list_for_user(user_id, limit, offset, unread_only)

    async def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        n = await self._repo.get_by_id(notification_id)
        if n is None:
            raise NotFoundError("Notification not found.")
        if n.user_id != user_id:
            raise PermissionDeniedError()
        n.is_read = True
        n.read_at = datetime.now(UTC)
        async with atomic(self._repo._session):
            await self._repo.save(n)
        return n

    async def mark_all_read(self, user_id: uuid.UUID) -> None:
        async with atomic(self._repo._session):
            await self._repo.mark_all_read(user_id)
