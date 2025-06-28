import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from test_utils import UserToken

from api.dependencies import crypto_hash_factory


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_user_unauthorized(client: AsyncClient, user_token: UserToken):
    payload = {
        "username": "test_user",
        "name": "Test User",
        "password": "password",
        "telegram_id": 0,
    }

    # without token
    response = await client.post("/api/v1/users/", json=payload)
    assert response.status_code == 403

    # wrong token
    headers = {"TOKEN": "wrong token"}
    response = await client.post("/api/v1/users/", json=payload, headers=headers)
    assert response.status_code == 401

    # unprivileged user
    headers = {"TOKEN": user_token["token"]}
    response = await client.post("/api/v1/users/", json=payload, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_user(client: AsyncClient, session: AsyncSession, super_user_token: UserToken):
    # success
    payload = {
        "username": "test_user",
        "password": "password",
        "telegram_id": 1,
    }
    headers = {"TOKEN": super_user_token["token"]}
    response = await client.post("/api/v1/users/", json=payload, headers=headers)
    assert response.status_code == 200
    result = await session.execute(text("SELECT * FROM users WHERE username='test_user'"))
    user = result.mappings().one()
    result = response.json()

    # check response
    assert result["id"] == user["id"]
    assert result["username"] == user["username"]

    # check db record
    assert user["username"] == payload["username"]

    # check hashed password
    crypto_hash = crypto_hash_factory()
    assert crypto_hash.verify(payload["password"], user["hashed_password"])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_login(client: AsyncClient, user_token: UserToken):
    payload = dict(
        username="wrong_user",
        password="wrong_password",
    )
    response = await client.post("/api/v1/users/login", json=payload)
    assert response.status_code == 401

    payload = dict(
        username="Authorized user",
        password="password",
    )
    response = await client.post("/api/v1/users/login", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result.get("token")
    assert isinstance(result["token"], str)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_user_password(client: AsyncClient, user_token: UserToken):
    # without token
    response = await client.post("/api/v1/users/update_password", json={})
    assert response.status_code == 403

    # wrong token
    headers = {"TOKEN": "wrong token"}
    response = await client.post("/api/v1/users/update_password", json={}, headers=headers)
    assert response.status_code == 401

    # wrong password
    payload = dict(
        old_password="wrong old password",
        new_password="new_password",
    )
    headers = {"TOKEN": user_token["token"]}
    response = await client.post("/api/v1/users/update_password", json=payload, headers=headers)
    assert response.status_code == 401

    # success
    payload = dict(
        old_password="password",
        new_password="new_password",
    )
    headers = {"TOKEN": user_token["token"]}
    response = await client.post("/api/v1/users/update_password", json=payload, headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == user_token["user"].id
    assert result["username"] == user_token["user"].username
