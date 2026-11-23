import uuid
from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import TokenType
from app.core.exceptions import (
    AccountInactiveError,
    AuthenticationError,
    PermissionDeniedError,
)
from app.core.permissions import Permission
from app.core.security import decode_token
from app.infrastructure.cache.redis import is_token_blacklisted
from app.infrastructure.database.session import get_db_session
from app.modules.identity.models import User
from app.modules.identity.repository import UserRepository

_bearer = HTTPBearer(auto_error=False)


async def _get_session():
    async with get_db_session() as session:
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer)],
    session: Annotated[AsyncSession, Depends(_get_session)],
) -> User:
    if not credentials:
        raise AuthenticationError("Authorization header missing.")

    payload = decode_token(credentials.credentials, TokenType.ACCESS)

    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise AuthenticationError("Token has been revoked.")

    user_id = uuid.UUID(payload["sub"])
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise AuthenticationError("User not found.")
    if not user.is_active:
        raise AccountInactiveError()

    # Attach permissions from token to user object for authorization checks
    user._token_permissions = set(payload.get("permissions", []))  # type: ignore[attr-defined]
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(*permissions: Permission):
    """Return a dependency that enforces all listed permissions on the current user."""

    async def _check(user: CurrentUser) -> User:
        user_perms: set[str] = getattr(user, "_token_permissions", set())
        for perm in permissions:
            if perm not in user_perms and not user.is_superuser:
                raise PermissionDeniedError(f"Permission '{perm}' is required.")
        return user

    return Depends(_check)
