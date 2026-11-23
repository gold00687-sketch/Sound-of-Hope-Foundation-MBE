import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.staff.models import StaffMember
from app.modules.staff.repository import StaffRepository
from app.modules.staff.schemas import StaffCreate, StaffUpdate


class StaffService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = StaffRepository(session)

    async def create(self, data: StaffCreate) -> StaffMember:
        existing = await self._repo.get_by_user_id(data.user_id)
        if existing:
            raise ConflictError("This user already has a staff record.")
        staff = StaffMember(**data.model_dump())
        async with atomic(self._repo._session):
            await self._repo.save(staff)
        return staff

    async def get(self, staff_id: uuid.UUID) -> StaffMember:
        staff = await self._repo.get_by_id(staff_id)
        if staff is None:
            raise NotFoundError("Staff record not found.")
        return staff

    async def list_staff(
        self,
        limit: int,
        offset: int,
        department_id: uuid.UUID | None = None,
        is_active: bool | None = None,
    ):
        return await self._repo.list_staff(limit, offset, department_id, is_active)

    async def update(self, staff_id: uuid.UUID, data: StaffUpdate) -> StaffMember:
        staff = await self._repo.get_by_id(staff_id)
        if staff is None:
            raise NotFoundError("Staff record not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(staff, field, value)
        async with atomic(self._repo._session):
            await self._repo.save(staff)
        return staff
