import pytest

from app.core.security import (
    create_token,
    decode_token,
    hash_password,
    password_needs_rehash,
    verify_password,
)
from app.core.constants import TokenType
from app.core.exceptions import TokenExpiredError, TokenInvalidError


def test_password_round_trip() -> None:
    hashed = hash_password("MySecret1!")
    assert verify_password("MySecret1!", hashed)
    assert not verify_password("WrongPass1!", hashed)


def test_password_needs_rehash() -> None:
    hashed = hash_password("SomePass1!")
    assert not password_needs_rehash(hashed)


def test_access_token_round_trip(monkeypatch) -> None:
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret-key-32chars-long!!")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://x:x@localhost/x")

    from app.core.config import get_settings
    get_settings.cache_clear()

    token = create_token(subject="user-123", token_type=TokenType.ACCESS)
    payload = decode_token(token, TokenType.ACCESS)
    assert payload["sub"] == "user-123"
    assert payload["type"] == TokenType.ACCESS


def test_token_type_mismatch(monkeypatch) -> None:
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret-key-32chars-long!!")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://x:x@localhost/x")

    from app.core.config import get_settings
    get_settings.cache_clear()

    token = create_token(subject="user-123", token_type=TokenType.REFRESH)
    with pytest.raises(TokenInvalidError):
        decode_token(token, TokenType.ACCESS)
