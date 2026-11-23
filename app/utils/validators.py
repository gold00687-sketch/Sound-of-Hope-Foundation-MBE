import re

_PHONE_RE = re.compile(r"^\+?[1-9]\d{6,14}$")
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def is_valid_phone(value: str) -> bool:
    return bool(_PHONE_RE.match(value.strip()))


def is_valid_slug(value: str) -> bool:
    return bool(_SLUG_RE.match(value))


def normalise_phone(value: str) -> str:
    return re.sub(r"[\s\-()]", "", value.strip())


def normalise_email(value: str) -> str:
    return value.strip().lower()
