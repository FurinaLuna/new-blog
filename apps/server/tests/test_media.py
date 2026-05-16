import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import io


@pytest.mark.asyncio
async def test_list_media_requires_auth(async_client, db_session, redis_mock):
    response = await async_client.get("/api/v1/admin/media")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_media_with_auth(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.get(
        "/api/v1/admin/media",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_upload_media_requires_auth(async_client, db_session, redis_mock):
    response = await async_client.post("/api/v1/admin/media/upload")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_media_requires_auth(async_client, db_session, redis_mock):
    response = await async_client.delete("/api/v1/admin/media/non-existent-id")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_non_existent_media(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.delete(
        "/api/v1/admin/media/non-existent-id",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_svg_blocked(async_client, db_session, redis_mock, auth_headers):
    file_content = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>'
    file = io.BytesIO(file_content)
    response = await async_client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.svg", file, "image/svg+xml")},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_unsupported_type(async_client, db_session, redis_mock, auth_headers):
    file_content = b'#!/bin/bash\necho hello'
    file = io.BytesIO(file_content)
    response = await async_client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.sh", file, "application/x-sh")},
        headers=auth_headers,
    )
    assert response.status_code == 400
