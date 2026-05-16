import pytest


@pytest.mark.asyncio
async def test_health_check(async_client, db_session, redis_mock):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "uptime_seconds" in data


@pytest.mark.asyncio
async def test_liveness_probe(async_client, db_session, redis_mock):
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_probe(async_client, db_session, redis_mock):
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data


@pytest.mark.asyncio
async def test_health_check_has_version(async_client, db_session, redis_mock):
    response = await async_client.get("/health")
    data = response.json()
    assert "version" in data
    assert data["version"] == "1.0.0"
