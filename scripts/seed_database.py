"""Seed the database with initial reference data (roles, permissions).

Usage:
    python -m scripts.seed_database
"""

import asyncio

from app.core.permissions import (
    ADMIN_PERMISSIONS,
    INSTRUCTOR_PERMISSIONS,
    PARTICIPANT_PERMISSIONS,
    PROGRAMME_MANAGER_PERMISSIONS,
    STAFF_PERMISSIONS,
)
from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.transaction import atomic
from app.modules.identity.models import Role, RolePermission
from app.modules.identity.repository import RoleRepository

ROLES = [
    {
        "name": "system_admin",
        "display_name": "System Administrator",
        "description": "Full system access.",
        "permissions": ADMIN_PERMISSIONS,
        "is_system": True,
    },
    {
        "name": "programme_manager",
        "display_name": "Programme Manager",
        "description": "Manages programmes, enrolments and participant records.",
        "permissions": PROGRAMME_MANAGER_PERMISSIONS,
        "is_system": True,
    },
    {
        "name": "instructor",
        "display_name": "Instructor",
        "description": "Delivers courses and records attendance and assessments.",
        "permissions": INSTRUCTOR_PERMISSIONS,
        "is_system": True,
    },
    {
        "name": "staff",
        "display_name": "Staff",
        "description": "General staff with read access across modules.",
        "permissions": STAFF_PERMISSIONS,
        "is_system": True,
    },
    {
        "name": "participant",
        "display_name": "Participant",
        "description": "Programme participant with limited read access.",
        "permissions": PARTICIPANT_PERMISSIONS,
        "is_system": True,
    },
]


async def seed() -> None:
    async with get_db_session() as session:
        repo = RoleRepository(session)
        for role_def in ROLES:
            existing = await repo.get_by_name(role_def["name"])
            if existing:
                print(f"Role '{role_def['name']}' already exists, skipping.")
                continue

            role = Role(
                name=role_def["name"],
                display_name=role_def["display_name"],
                description=role_def.get("description"),
                is_system=role_def.get("is_system", False),
            )
            async with atomic(session):
                session.add(role)
                await session.flush()
                for perm_name in role_def["permissions"]:
                    perm = await repo.get_or_create_permission(str(perm_name))
                    session.add(RolePermission(role_id=role.id, permission_id=perm.id))

            print(f"Created role: {role_def['name']}")


if __name__ == "__main__":
    asyncio.run(seed())
