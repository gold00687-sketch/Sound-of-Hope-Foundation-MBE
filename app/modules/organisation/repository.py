import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organisation.models import Department, Organisation


class OrganisationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self) -> Organisation | None:
        result = await self._session.execute(select(Organisation).limit(1))
        return result.scalar_one_or_none()

    async def save(self, org: Organisation) -> Organisation:
        self._session.add(org)
        await self._session.flush()
        return org


class DepartmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, dept_id: uuid.UUID) -> Department | None:
        result = await self._session.execute(
            select(Department).where(Department.id == dept_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, include_inactive: bool = False) -> list[Department]:
        q = select(Department)
        if not include_inactive:
            q = q.where(Department.is_active == True)
        result = await self._session.execute(q.order_by(Department.name))
        return list(result.scalars().all())

    async def save(self, dept: Department) -> Department:
        self._session.add(dept)
        await self._session.flush()
        return dept
