"""Create the initial superuser account.

Usage:
    python -m scripts.create_initial_admin --email admin@example.com --password AdminPass1!
"""

import argparse
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.transaction import atomic
from app.modules.identity.models import Role, RolePermission, User, UserProfile, UserRole
from app.modules.identity.repository import RoleRepository, UserRepository
from app.core.permissions import ADMIN_PERMISSIONS, Permission


async def create_admin(email: str, password: str, first_name: str, last_name: str) -> None:
    async with get_db_session() as session:
        user_repo = UserRepository(session)
        role_repo = RoleRepository(session)

        existing = await user_repo.get_by_email(email)
        if existing:
            print(f"User {email} already exists.")
            return

        user = User(
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            is_email_verified=True,
            is_superuser=True,
        )
        profile = UserProfile(user=user, first_name=first_name, last_name=last_name)

        # Ensure system admin role exists
        admin_role = await role_repo.get_by_name("system_admin")
        if admin_role is None:
            admin_role = Role(
                name="system_admin",
                display_name="System Administrator",
                description="Full access to all system features.",
                is_system=True,
            )
            async with atomic(session):
                session.add(admin_role)
                await session.flush()

                for perm_name in ADMIN_PERMISSIONS:
                    perm = await role_repo.get_or_create_permission(str(perm_name))
                    session.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))

        async with atomic(session):
            await user_repo.create(user, profile)
            await role_repo.assign_role_to_user(user.id, admin_role.id)

        print(f"Admin account created: {email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create initial admin user")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--first-name", default="System")
    parser.add_argument("--last-name", default="Admin")
    args = parser.parse_args()

    asyncio.run(create_admin(args.email, args.password, args.first_name, args.last_name))


if __name__ == "__main__":
    main()
