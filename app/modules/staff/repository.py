import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.staff.models import StaffMember


class StaffRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, staff_id: uuid.UUID) -> StaffMember | None:
        result = await self._session.execute(
            select(StaffMember).where(StaffMember.id == staff_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> StaffMember | None:
        result = await self._session.execute(
            select(StaffMember).where(StaffMember.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_staff(
        self,
        limit: int,
        offset: int,
        department_id: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[StaffMember], int]:
        q = select(StaffMember)
        count_q = select(func.count()).select_from(StaffMember)

        if department_id is not None:
            q = q.where(StaffMember.department_id == department_id)
            count_q = count_q.where(StaffMember.department_id == department_id)
        if is_active is not None:
            q = q.where(StaffMember.is_active == is_active)
            count_q = count_q.where(StaffMember.is_active == is_active)

        total = (await self._session.execute(count_q)).scalar_one()
        result = await self._session.execute(
            q.order_by(StaffMember.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def save(self, staff: StaffMember) -> StaffMember:
        self._session.add(staff)
        await self._session.flush()
        return staff
