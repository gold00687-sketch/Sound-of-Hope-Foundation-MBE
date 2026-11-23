import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.infrastructure.database.transaction import atomic
from app.modules.organisation.models import Department, Organisation
from app.modules.organisation.repository import DepartmentRepository, OrganisationRepository
from app.modules.organisation.schemas import DepartmentCreate, DepartmentUpdate, OrganisationUpdate


class OrganisationService:
    def __init__(self, session: AsyncSession) -> None:
        self._org_repo = OrganisationRepository(session)
        self._dept_repo = DepartmentRepository(session)

    async def get_organisation(self) -> Organisation:
        org = await self._org_repo.get()
        if org is None:
            raise NotFoundError("Organisation profile has not been configured yet.")
        return org

    async def update_organisation(self, data: OrganisationUpdate) -> Organisation:
        org = await self._org_repo.get()
        if org is None:
            # First-time setup
            org = Organisation(**{k: v for k, v in data.model_dump().items() if v is not None})
            if not org.name:
                raise NotFoundError("Organisation name is required for initial setup.")
        else:
            for field, value in data.model_dump(exclude_none=True).items():
                setattr(org, field, value)
        async with atomic(self._org_repo._session):
            await self._org_repo.save(org)
        return org

    async def list_departments(self, include_inactive: bool = False) -> list[Department]:
        return await self._dept_repo.list_all(include_inactive)

    async def create_department(self, data: DepartmentCreate) -> Department:
        org = await self._org_repo.get()
        if org is None:
            raise NotFoundError("Organisation must be configured before creating departments.")
        dept = Department(
            organisation_id=org.id,
            name=data.name,
            code=data.code,
            description=data.description,
            parent_id=data.parent_id,
        )
        async with atomic(self._dept_repo._session):
            await self._dept_repo.save(dept)
        return dept

    async def update_department(self, dept_id: uuid.UUID, data: DepartmentUpdate) -> Department:
        dept = await self._dept_repo.get_by_id(dept_id)
        if dept is None:
            raise NotFoundError("Department not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(dept, field, value)
        async with atomic(self._dept_repo._session):
            await self._dept_repo.save(dept)
        return dept
