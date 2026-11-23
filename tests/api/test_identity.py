"""API-level tests for identity endpoints."""

import pytest
from httpx import AsyncClient


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"
CHANGE_PW_URL = "/api/v1/auth/password/change"
RESET_PW_URL = "/api/v1/auth/password/reset"


VALID_USER = {
    "email": "alice@example.com",
    "password": "Secure1234!",
    "first_name": "Alice",
    "last_name": "Smith",
}


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(REGISTER_URL, json=VALID_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == VALID_USER["email"]
    assert data["first_name"] == "Alice"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(REGISTER_URL, json=VALID_USER)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient) -> None:
    payload = {**VALID_USER, "email": "bob@example.com", "password": "short"}
    response = await client.post(REGISTER_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(
        LOGIN_URL, json={"email": VALID_USER["email"], "password": VALID_USER["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(
        LOGIN_URL, json={"email": VALID_USER["email"], "password": "WrongPass1!"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    response = await client.post(
        LOGIN_URL, json={"email": "nobody@example.com", "password": "Anything1!"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient) -> None:
    response = await client.get(ME_URL)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    login = await client.post(
        LOGIN_URL, json={"email": VALID_USER["email"], "password": VALID_USER["password"]}
    )
    token = login.json()["access_token"]
    response = await client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == VALID_USER["email"]


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    login = await client.post(
        LOGIN_URL, json={"email": VALID_USER["email"], "password": VALID_USER["password"]}
    )
    refresh_token = login.json()["refresh_token"]
    response = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient) -> None:
    response = await client.post(REFRESH_URL, json={"refresh_token": "not-a-real-token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_password_reset_does_not_reveal_existence(client: AsyncClient) -> None:
    response = await client.post(RESET_PW_URL, json={"email": "doesnotexist@example.com"})
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
