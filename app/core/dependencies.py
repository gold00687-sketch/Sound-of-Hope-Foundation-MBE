from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
)
from app.core.permissions import Permission
from app.core.security import decode_token
from app.core.constants import TokenType
from app.infrastructure.database.session import get_db_session

_bearer = HTTPBearer(auto_error=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _extract_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    if not credentials:
        raise AuthenticationError("Authorization header missing.")
    return credentials.credentials


async def get_current_user_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer)],
) -> dict:
    token = _extract_token(credentials)
    payload = decode_token(token, TokenType.ACCESS)
    return payload


CurrentUserPayload = Annotated[dict, Depends(get_current_user_payload)]


def require_permissions(*permissions: Permission):
    """Return a dependency that enforces all listed permissions."""

    async def _check(payload: CurrentUserPayload) -> dict:
        user_permissions: list[str] = payload.get("permissions", [])
        for perm in permissions:
            if perm not in user_permissions:
                raise PermissionDeniedError(
                    f"Permission '{perm}' is required."
                )
        return payload

    return Depends(_check)


def require_any_permission(*permissions: Permission):
    """Return a dependency that requires at least one of the listed permissions."""

    async def _check(payload: CurrentUserPayload) -> dict:
        user_permissions: set[str] = set(payload.get("permissions", []))
        if not user_permissions.intersection(permissions):
            raise PermissionDeniedError(
                "Insufficient permissions."
            )
        return payload

    return Depends(_check)
