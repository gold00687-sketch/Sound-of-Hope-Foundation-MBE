from fastapi import APIRouter

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.analytics.service import AnalyticsService

router = APIRouter()


@router.get(
    "/summary",
    dependencies=[require_permission(Permission.ANALYTICS_READ)],
    summary="Aggregated organisation-wide dashboard statistics",
)
async def get_summary(session: SessionDep) -> dict:
    """
    Returns live counts for all major entities.
    Intentionally returns a plain dict so the schema can evolve without
    a migration — the front-end reads keys by name.
    """
    return await AnalyticsService(session).get_summary()
