import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.infrastructure.database.base import Base

# Every model module must be imported here so Alembic detects schema changes.
import app.modules.identity.models          # noqa: F401
import app.modules.users.models             # noqa: F401
import app.modules.organisation.models      # noqa: F401
import app.modules.staff.models             # noqa: F401
import app.modules.participants.models      # noqa: F401
import app.modules.guardians.models         # noqa: F401
import app.modules.programmes.models        # noqa: F401
import app.modules.projects.models          # noqa: F401
import app.modules.applications.models      # noqa: F401
import app.modules.enrolments.models        # noqa: F401
import app.modules.courses.models           # noqa: F401
import app.modules.classes.models           # noqa: F401
import app.modules.schedules.models         # noqa: F401
import app.modules.attendance.models        # noqa: F401
import app.modules.assessments.models       # noqa: F401
import app.modules.certificates.models      # noqa: F401
import app.modules.creative_arts.models     # noqa: F401
import app.modules.vocational_training.models  # noqa: F401
import app.modules.instruments.models       # noqa: F401
import app.modules.events.models            # noqa: F401
import app.modules.community.models         # noqa: F401
import app.modules.discussions.models       # noqa: F401
import app.modules.moderation.models        # noqa: F401
import app.modules.safeguarding.models      # noqa: F401
import app.modules.consent.models           # noqa: F401
import app.modules.referrals.models         # noqa: F401
import app.modules.research.models          # noqa: F401
import app.modules.library.models           # noqa: F401
import app.modules.publications.models      # noqa: F401
import app.modules.cms.models               # noqa: F401
import app.modules.media.models             # noqa: F401
import app.modules.navigation.models        # noqa: F401
import app.modules.finance.models           # noqa: F401
import app.modules.donations.models         # noqa: F401
import app.modules.payments.models          # noqa: F401
import app.modules.expenses.models          # noqa: F401
import app.modules.notifications.models     # noqa: F401
import app.modules.messaging.models         # noqa: F401
import app.modules.reporting.models         # noqa: F401
import app.modules.analytics.models         # noqa: F401
import app.modules.audit.models             # noqa: F401

config = context.config
fileConfig(config.config_file_name)

from app.core.config import get_settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"ssl": False} if settings.is_development else {},
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
