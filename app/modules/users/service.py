import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.infrastructure.database.transaction import atomic
from app.modules.users.models import UserAddress, UserEmergencyContact
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    EmergencyContactCreate,
    ProfileUpdateRequest,
    UserAddressCreate,
)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def get_user(self, user_id: uuid.UUID):
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return user

    async def list_users(self, limit: int, offset: int, search: str | None, is_active: bool | None):
        return await self._repo.list_users(limit, offset, search, is_active)

    async def update_profile(
        self, user_id: uuid.UUID, data: ProfileUpdateRequest, requesting_user_id: uuid.UUID
    ):
        if user_id != requesting_user_id:
            raise PermissionDeniedError("You can only update your own profile.")
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        profile = user.profile
        if data.first_name is not None:
            profile.first_name = data.first_name
        if data.last_name is not None:
            profile.last_name = data.last_name
        if data.display_name is not None:
            profile.display_name = data.display_name
        if data.bio is not None:
            profile.bio = data.bio
        async with atomic(self._repo._session):
            await self._repo.save_profile(profile)
        return user

    async def deactivate_user(self, user_id: uuid.UUID) -> None:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        async with atomic(self._repo._session):
            user.is_active = False
            await self._repo.save(user)

    async def activate_user(self, user_id: uuid.UUID) -> None:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        async with atomic(self._repo._session):
            user.is_active = True
            await self._repo.save(user)

    async def add_address(self, user_id: uuid.UUID, data: UserAddressCreate) -> UserAddress:
        async with atomic(self._repo._session):
            address = UserAddress(user_id=user_id, **data.model_dump())
            return await self._repo.add_address(address)

    async def add_emergency_contact(
        self, user_id: uuid.UUID, data: EmergencyContactCreate
    ) -> UserEmergencyContact:
        async with atomic(self._repo._session):
            contact = UserEmergencyContact(user_id=user_id, **data.model_dump())
            return await self._repo.add_emergency_contact(contact)
