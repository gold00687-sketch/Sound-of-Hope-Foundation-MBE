import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
def mock_redis_cache():
    """Replace Redis cache calls with no-ops for unit/api tests."""
    _store: dict[str, str] = {}

    async def _get(key: str) -> str | None:
        return _store.get(key)

    async def _set(key: str, value: str, ttl: int | None = None) -> None:
        _store[key] = value

    async def _delete(key: str) -> None:
        _store.pop(key, None)

    async def _blacklist(jti: str, ttl: int) -> None:
        _store[f"revoked_token:{jti}"] = "1"

    async def _is_blacklisted(jti: str) -> bool:
        return f"revoked_token:{jti}" in _store

    with (
        patch("app.infrastructure.cache.redis.cache_get", side_effect=_get),
        patch("app.infrastructure.cache.redis.cache_set", side_effect=_set),
        patch("app.infrastructure.cache.redis.cache_delete", side_effect=_delete),
        patch("app.infrastructure.cache.redis.blacklist_token", side_effect=_blacklist),
        patch("app.infrastructure.cache.redis.is_token_blacklisted", side_effect=_is_blacklisted),
        # Also patch the imports that modules have already resolved
        patch("app.modules.identity.service.cache_get", side_effect=_get),
        patch("app.modules.identity.service.cache_set", side_effect=_set),
        patch("app.modules.identity.service.cache_delete", side_effect=_delete),
        patch("app.modules.identity.service.blacklist_token", side_effect=_blacklist),
        patch("app.modules.identity.service.is_token_blacklisted", side_effect=_is_blacklisted),
        patch("app.modules.identity.dependencies.is_token_blacklisted", side_effect=_is_blacklisted),
        # Suppress email task dispatches
        patch("app.modules.identity.service.IdentityService._send_verification_email", new=AsyncMock()),
    ):
        yield _store


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, mock_redis_cache) -> AsyncGenerator[AsyncClient, None]:
    from app.core.dependencies import get_session

    @asynccontextmanager
    async def _null_lifespan(app):
        yield

    from app.main import create_app
    app = create_app()
    app.router.lifespan_context = _null_lifespan

    async def override_session():
        yield db_session

    app.dependency_overrides[get_session] = override_session

    from app.modules.identity import dependencies as id_deps
    app.dependency_overrides[id_deps._get_session] = override_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
