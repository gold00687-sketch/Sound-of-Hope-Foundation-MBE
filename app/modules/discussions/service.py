from sqlalchemy.ext.asyncio import AsyncSession


class DiscussionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
