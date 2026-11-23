import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.identity.models import User, UserProfile
from app.modules.users.models import UserAddress, UserEmergencyContact


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        q = select(User).options(selectinload(User.profile))
        count_q = select(func.count()).select_from(User)

        if is_active is not None:
            q = q.where(User.is_active == is_active)
            count_q = count_q.where(User.is_active == is_active)

        if search:
            pattern = f"%{search}%"
            from sqlalchemy import or_
            q = q.join(UserProfile, UserProfile.user_id == User.id).where(
                or_(
                    User.email.ilike(pattern),
                    UserProfile.first_name.ilike(pattern),
                    UserProfile.last_name.ilike(pattern),
                )
            )
            count_q = count_q.join(UserProfile, UserProfile.user_id == User.id).where(
                or_(
                    User.email.ilike(pattern),
                    UserProfile.first_name.ilike(pattern),
                    UserProfile.last_name.ilike(pattern),
                )
            )

        total_result = await self._session.execute(count_q)
        total = total_result.scalar_one()

        q = q.order_by(User.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(q)
        return list(result.scalars().all()), total

    async def save(self, user: User) -> None:
        self._session.add(user)
        await self._session.flush()

    async def save_profile(self, profile: UserProfile) -> None:
        self._session.add(profile)
        await self._session.flush()

    async def get_addresses(self, user_id: uuid.UUID) -> list[UserAddress]:
        result = await self._session.execute(
            select(UserAddress).where(UserAddress.user_id == user_id)
        )
        return list(result.scalars().all())

    async def add_address(self, address: UserAddress) -> UserAddress:
        self._session.add(address)
        await self._session.flush()
        return address

    async def get_emergency_contacts(self, user_id: uuid.UUID) -> list[UserEmergencyContact]:
        result = await self._session.execute(
            select(UserEmergencyContact).where(UserEmergencyContact.user_id == user_id)
        )
        return list(result.scalars().all())

    async def add_emergency_contact(self, contact: UserEmergencyContact) -> UserEmergencyContact:
        self._session.add(contact)
        await self._session.flush()
        return contact
