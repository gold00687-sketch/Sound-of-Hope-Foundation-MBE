from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def atomic(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Execute the wrapped block in a single database transaction.

    Uses a SAVEPOINT (begin_nested) so it works even if a transaction
    is already in progress from a prior read query on the same session.
    Commits on success, rolls back on any exception.
    """
    async with session.begin_nested():
        yield session
    await session.commit()
