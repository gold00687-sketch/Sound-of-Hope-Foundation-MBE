"""API tests for programmes and enrolments."""

import pytest
from httpx import AsyncClient

AUTH_URL = "/api/v1/auth"
PROGRAMMES_URL = "/api/v1/programmes"
PARTICIPANTS_URL = "/api/v1/participants"
ENROLMENTS_URL = "/api/v1/enrolments"

STAFF_USER = {
    "email": "manager@example.com",
    "password": "Manager1234!",
    "first_name": "Programme",
    "last_name": "Manager",
}


async def _register_and_login(client: AsyncClient, user: dict) -> str:
    await client.post(f"{AUTH_URL}/register", json=user)
    resp = await client.post(
        f"{AUTH_URL}/login",
        json={"email": user["email"], "password": user["password"]},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_programmes_public(client: AsyncClient) -> None:
    response = await client.get(PROGRAMMES_URL)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "meta" in data


@pytest.mark.asyncio
async def test_create_programme_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        PROGRAMMES_URL,
        json={"name": "Test Programme", "requires_application": True},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_participants_requires_auth(client: AsyncClient) -> None:
    response = await client.get(PARTICIPANTS_URL)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_enrolment_requires_auth(client: AsyncClient) -> None:
    import uuid
    response = await client.post(
        ENROLMENTS_URL,
        json={
            "programme_id": str(uuid.uuid4()),
            "participant_id": str(uuid.uuid4()),
            "enrolment_date": "2026-01-01",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_programme_categories_public(client: AsyncClient) -> None:
    response = await client.get(f"{PROGRAMMES_URL}/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
