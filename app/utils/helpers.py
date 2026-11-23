import re
import secrets
import string
import uuid


def generate_token(length: int = 64) -> str:
    return secrets.token_urlsafe(length)


def generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()
