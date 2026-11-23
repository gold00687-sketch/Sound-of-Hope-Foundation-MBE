from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_pre_ping=True,
            echo=settings.is_development,
            # Disable SSL for local dev — asyncpg's SSL negotiation can break
            # SCRAM-SHA-256 auth when connecting to a Docker postgres on Windows.
            connect_args={"ssl": False} if settings.is_development else {},
        )
    return _engine


async def close_engine() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
