import pytest
from app.core.security import create_access_token, create_refresh_token, hash_password


@pytest.mark.asyncio
async def test_login_success(async_client, db_session, redis_mock, sample_user):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client, db_session, redis_mock, sample_user):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_rate_limit(async_client, db_session, redis_mock, sample_user):
    for _ in range(5):
        await async_client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword1"},
        )
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_logout_blacklists_token(async_client, redis_mock, auth_headers):
    response = await async_client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_token(async_client, redis_mock):
    token_data = {"sub": "test-user-id", "username": "admin"}
    refresh_token = create_refresh_token(token_data)
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_change_password(async_client, db_session, redis_mock, sample_user):
    token_data = {"sub": sample_user.id, "username": sample_user.username}
    access_token = create_access_token(token_data)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "admin123", "new_password": "newpassword1"},
        headers=headers,
    )
    assert response.status_code == 200
