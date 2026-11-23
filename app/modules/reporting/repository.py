from sqlalchemy.ext.asyncio import AsyncSession


class ReportingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
