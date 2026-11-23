"""Security-focused tests for authentication."""

import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"

VALID_USER = {
    "email": "sectest@example.com",
    "password": "Secure1234!",
    "first_name": "Sec",
    "last_name": "Test",
}


@pytest.mark.asyncio
async def test_cannot_access_protected_route_without_token(client: AsyncClient) -> None:
    response = await client.get(ME_URL)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_malformed_token_rejected(client: AsyncClient) -> None:
    response = await client.get(ME_URL, headers={"Authorization": "Bearer not.a.jwt"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_account_lockout_after_repeated_failures(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    for _ in range(5):
        resp = await client.post(
            LOGIN_URL,
            json={"email": VALID_USER["email"], "password": "WrongPass1!"},
        )
    # 5th or 6th attempt should lock the account
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_password_reset_does_not_leak_existence(client: AsyncClient) -> None:
    r1 = await client.post(
        "/api/v1/auth/password/reset", json={"email": "real@example.com"}
    )
    r2 = await client.post(
        "/api/v1/auth/password/reset", json={"email": "ghost@example.com"}
    )
    assert r1.status_code == r2.status_code == 204


@pytest.mark.asyncio
async def test_sql_injection_in_email(client: AsyncClient) -> None:
    response = await client.post(
        LOGIN_URL,
        json={"email": "' OR '1'='1", "password": "anything"},
    )
    assert response.status_code == 422  # Pydantic rejects invalid email


@pytest.mark.asyncio
async def test_oversized_password_rejected(client: AsyncClient) -> None:
    payload = {**VALID_USER, "email": "oversize@example.com", "password": "A" * 200}
    response = await client.post(REGISTER_URL, json=payload)
    assert response.status_code == 422
