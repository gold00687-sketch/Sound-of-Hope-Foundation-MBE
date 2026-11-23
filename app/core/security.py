from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.constants import TokenType
from app.core.exceptions import TokenExpiredError, TokenInvalidError

_ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError):
        return False


def password_needs_rehash(hashed: str) -> bool:
    return _ph.check_needs_rehash(hashed)


def create_token(
    subject: str,
    token_type: TokenType,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)

    if expires_delta is None:
        if token_type == TokenType.ACCESS:
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
        elif token_type == TokenType.REFRESH:
            expires_delta = timedelta(days=settings.refresh_token_expire_days)
        elif token_type == TokenType.EMAIL_VERIFICATION:
            expires_delta = timedelta(hours=24)
        elif token_type == TokenType.PASSWORD_RESET:
            expires_delta = timedelta(hours=1)
        else:
            expires_delta = timedelta(hours=1)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        # jose raises ExpiredSignatureError (a subclass of JWTError) for expired tokens
        if "expired" in str(exc).lower():
            raise TokenExpiredError() from exc
        raise TokenInvalidError() from exc

    if payload.get("type") != expected_type:
        raise TokenInvalidError("Token type mismatch.")

    return payload
