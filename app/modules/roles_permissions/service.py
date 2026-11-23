import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.infrastructure.database.transaction import atomic
from app.modules.identity.models import Permission, Role, RolePermission, UserRole
from app.modules.identity.repository import RoleRepository, UserRepository
from app.modules.roles_permissions.schemas import AssignPermissionsRequest, RoleCreate, RoleUpdate


class RolesPermissionsService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = RoleRepository(session)
        self._user_repo = UserRepository(session)
        self._session = session

    async def list_roles(self) -> list[Role]:
        return await self._repo.list_all()

    async def create_role(self, data: RoleCreate) -> Role:
        existing = await self._repo.get_by_name(data.name)
        if existing:
            raise ConflictError(f"Role '{data.name}' already exists.")
        role = Role(name=data.name, display_name=data.display_name, description=data.description)
        async with atomic(self._session):
            await self._repo.create(role)
        return role

    async def update_role(self, role_id: uuid.UUID, data: RoleUpdate) -> Role:
        result = await self._session.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if role is None:
            raise NotFoundError("Role not found.")
        if role.is_system:
            raise ValidationError("System roles cannot be modified.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(role, field, value)
        async with atomic(self._session):
            self._session.add(role)
            await self._session.flush()
        return role

    async def assign_permissions(self, role_id: uuid.UUID, data: AssignPermissionsRequest) -> Role:
        result = await self._session.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if role is None:
            raise NotFoundError("Role not found.")
        async with atomic(self._session):
            await self._session.execute(
                delete(RolePermission).where(RolePermission.role_id == role_id)
            )
            for perm_name in data.permission_names:
                perm = await self._repo.get_or_create_permission(perm_name)
                self._session.add(RolePermission(role_id=role_id, permission_id=perm.id))
        return role

    async def assign_role_to_user(
        self, user_id: uuid.UUID, role_name: str, granted_by_id: uuid.UUID
    ) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        role = await self._repo.get_by_name(role_name)
        if role is None:
            raise NotFoundError(f"Role '{role_name}' not found.")
        async with atomic(self._session):
            await self._repo.assign_role_to_user(user_id, role.id, granted_by_id)

    async def remove_role_from_user(self, user_id: uuid.UUID, role_name: str) -> None:
        role = await self._repo.get_by_name(role_name)
        if role is None:
            raise NotFoundError(f"Role '{role_name}' not found.")
        async with atomic(self._session):
            await self._session.execute(
                delete(UserRole).where(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role.id,
                )
            )

    async def list_user_roles(self, user_id: uuid.UUID) -> list[UserRole]:
        result = await self._session.execute(
            select(UserRole)
            .options(selectinload(UserRole.role))
            .where(UserRole.user_id == user_id)
        )
        return list(result.scalars().all())
