from sqlalchemy.ext.asyncio import AsyncSession


class ResearchService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
