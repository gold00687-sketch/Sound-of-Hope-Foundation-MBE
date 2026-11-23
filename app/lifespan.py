from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.core.config import get_settings
from app.infrastructure.cache.redis import close_redis, get_redis
from app.infrastructure.database.connection import close_engine, get_engine

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info("startup", env=settings.app_env)

    # Warm up connections — fail fast if misconfigured
    engine = get_engine()
    async with engine.connect() as conn:
        await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    logger.info("database_connected")

    redis = get_redis()
    await redis.ping()
    logger.info("redis_connected")

    yield

    await close_engine()
    await close_redis()
    logger.info("shutdown_complete")
