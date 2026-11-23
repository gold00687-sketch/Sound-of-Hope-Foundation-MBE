from fastapi import APIRouter

from app.api.v1.router import v1_router

api_router = APIRouter()

api_router.include_router(v1_router, prefix="/api/v1")


@api_router.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok"}


@api_router.get("/ready", tags=["system"])
async def ready() -> dict:
    from app.infrastructure.cache.redis import get_redis
    from app.infrastructure.database.session import get_session_factory
    import sqlalchemy

    checks: dict[str, str] = {}

    try:
        factory = get_session_factory()
        async with factory() as session:
            await session.execute(sqlalchemy.text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"

    try:
        await get_redis().ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ready" if all_ok else "degraded", "checks": checks}
