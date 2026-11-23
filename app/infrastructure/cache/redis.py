from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        settings = get_settings()
        _client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    return _client


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def cache_get(key: str) -> str | None:
    try:
        return await get_redis().get(key)
    except Exception as exc:
        logger.warning("cache_get_failed", key=key, error=str(exc))
        return None


async def cache_set(key: str, value: str, ttl: int | None = None) -> None:
    settings = get_settings()
    effective_ttl = ttl if ttl is not None else settings.redis_cache_ttl
    try:
        await get_redis().setex(key, effective_ttl, value)
    except Exception as exc:
        logger.warning("cache_set_failed", key=key, error=str(exc))


async def cache_delete(key: str) -> None:
    try:
        await get_redis().delete(key)
    except Exception as exc:
        logger.warning("cache_delete_failed", key=key, error=str(exc))


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a glob pattern. Use with care in production."""
    try:
        client = get_redis()
        keys = [k async for k in client.scan_iter(pattern)]
        if keys:
            return await client.delete(*keys)
        return 0
    except Exception as exc:
        logger.warning("cache_delete_pattern_failed", pattern=pattern, error=str(exc))
        return 0


async def blacklist_token(jti: str, ttl: int) -> None:
    """Mark a JWT ID as revoked for the remainder of its natural lifetime."""
    await cache_set(f"revoked_token:{jti}", "1", ttl=ttl)


async def is_token_blacklisted(jti: str) -> bool:
    value = await cache_get(f"revoked_token:{jti}")
    return value is not None
