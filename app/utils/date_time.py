from datetime import UTC, date, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def age_in_years(dob: date, reference: date | None = None) -> int:
    ref = reference or datetime.now(UTC).date()
    years = ref.year - dob.year
    if (ref.month, ref.day) < (dob.month, dob.day):
        years -= 1
    return max(0, years)
