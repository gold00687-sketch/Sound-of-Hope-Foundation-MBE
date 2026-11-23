from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _count(self, table_name: str) -> int:
        """Fast COUNT(*) using raw SQL to avoid importing every model."""
        result = await self._session.execute(
            # text() not needed — table names are hard-coded, not user input
            select(func.count()).select_from(
                self._session.get_bind().dialect.identifier_preparer  # noqa
            )
        )
        # Fallback: execute raw count directly
        from sqlalchemy import text
        row = await self._session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))  # noqa: S608
        return row.scalar_one()

    async def get_summary(self) -> dict:
        from sqlalchemy import text

        async def count(table: str) -> int:
            try:
                row = await self._session.execute(text(f"SELECT COUNT(*) FROM {table}"))  # noqa: S608
                return row.scalar_one() or 0
            except Exception:
                return 0

        participants   = await count("participants")
        staff          = await count("staff")
        programmes     = await count("programmes")
        enrolments     = await count("enrolments")
        applications   = await count("applications")
        events         = await count("events")
        donations      = await count("donations")
        payments       = await count("payments")
        bookings       = await count("musician_bookings")
        publications   = await count("publications")
        certificates   = await count("certificates")

        # Pending sub-counts
        pending_applications = 0
        pending_bookings     = 0
        confirmed_bookings   = 0
        try:
            r = await self._session.execute(
                text("SELECT COUNT(*) FROM applications WHERE status = 'pending'")
            )
            pending_applications = r.scalar_one() or 0
        except Exception:
            pass
        try:
            r = await self._session.execute(
                text("SELECT COUNT(*) FROM musician_bookings WHERE status = 'pending'")
            )
            pending_bookings = r.scalar_one() or 0
            r2 = await self._session.execute(
                text("SELECT COUNT(*) FROM musician_bookings WHERE status = 'confirmed'")
            )
            confirmed_bookings = r2.scalar_one() or 0
        except Exception:
            pass

        return {
            "participants":          participants,
            "staff":                 staff,
            "programmes":            programmes,
            "enrolments":            enrolments,
            "applications":          applications,
            "pending_applications":  pending_applications,
            "events":                events,
            "donations":             donations,
            "payments":              payments,
            "bookings":              bookings,
            "pending_bookings":      pending_bookings,
            "confirmed_bookings":    confirmed_bookings,
            "publications":          publications,
            "certificates":          certificates,
        }
