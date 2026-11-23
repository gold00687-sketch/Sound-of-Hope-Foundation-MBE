import hashlib
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.identity.models import (
    AuthEvent,
    Permission,
    RefreshToken,
    Role,
    RolePermission,
    User,
    UserProfile,
    UserRole,
)


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.profile), selectinload(User.roles).selectinload(UserRole.role))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.profile), selectinload(User.roles).selectinload(UserRole.role))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self._session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def create(self, user: User, profile: UserProfile) -> User:
        self._session.add(user)
        self._session.add(profile)
        await self._session.flush()
        return user

    async def save(self, user: User) -> None:
        self._session.add(user)
        await self._session.flush()

    async def get_permissions_for_user(self, user_id: uuid.UUID) -> list[str]:
        result = await self._session.execute(
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return [row[0] for row in result.fetchall()]


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def create(self, token: RefreshToken) -> RefreshToken:
        self._session.add(token)
        await self._session.flush()
        return token

    async def get_by_token(self, raw_token: str) -> RefreshToken | None:
        token_hash = self._hash(raw_token)
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(UTC)
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        for t in result.scalars().all():
            t.revoked_at = datetime.now(UTC)
        await self._session.flush()


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_name(self, name: str) -> Role | None:
        result = await self._session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Role]:
        result = await self._session.execute(select(Role).order_by(Role.name))
        return list(result.scalars().all())

    async def create(self, role: Role) -> Role:
        self._session.add(role)
        await self._session.flush()
        return role

    async def get_or_create_permission(self, name: str) -> Permission:
        result = await self._session.execute(
            select(Permission).where(Permission.name == name)
        )
        perm = result.scalar_one_or_none()
        if perm is None:
            perm = Permission(name=name)
            self._session.add(perm)
            await self._session.flush()
        return perm

    async def assign_role_to_user(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        granted_by_id: uuid.UUID | None = None,
    ) -> None:
        existing = await self._session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id, UserRole.role_id == role_id
            )
        )
        if existing.scalar_one_or_none() is None:
            self._session.add(UserRole(user_id=user_id, role_id=role_id, granted_by_id=granted_by_id))
            await self._session.flush()


class AuthEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, event: AuthEvent) -> None:
        self._session.add(event)
        await self._session.flush()
