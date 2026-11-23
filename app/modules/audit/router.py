import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.audit.schemas import AuditLogResponse
from app.modules.audit.service import AuditService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get("", response_model=Page[AuditLogResponse],
            dependencies=[require_permission(Permission.AUDIT_READ)])
async def list_audit_logs(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    user_id: uuid.UUID | None = Query(default=None),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
):
    items, total = await AuditService(session).list_logs(
        pagination.limit, pagination.offset,
        user_id, action, resource_type, from_date, to_date,
    )
    return Page.create(items, pagination, total)
