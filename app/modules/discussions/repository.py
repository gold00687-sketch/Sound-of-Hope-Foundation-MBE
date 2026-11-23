from sqlalchemy.ext.asyncio import AsyncSession


class DiscussionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
