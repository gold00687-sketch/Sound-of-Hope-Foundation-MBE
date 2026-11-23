from sqlalchemy.ext.asyncio import AsyncSession


class VocationalService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
