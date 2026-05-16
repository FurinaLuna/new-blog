import pytest


@pytest.mark.asyncio
async def test_submit_events(async_client, db_session, redis_mock):
    response = await async_client.post(
        "/api/v1/analytics/events",
        json=[
            {
                "event_type": "page_view",
                "source_page": "/",
                "event_data": None,
                "session_id": "test-session-1",
            }
        ],
    )
    assert response.status_code == 201
    data = response.json()
    assert data["received"] == 1


@pytest.mark.asyncio
async def test_submit_multiple_events(async_client, db_session, redis_mock):
    response = await async_client.post(
        "/api/v1/analytics/events",
        json=[
            {"event_type": "page_view", "source_page": "/", "event_data": None, "session_id": "test-session-1"},
            {"event_type": "click", "source_page": "/post/test", "event_data": {"button": "share"}, "session_id": "test-session-1"},
        ],
    )
    assert response.status_code == 201
    data = response.json()
    assert data["received"] == 2


@pytest.mark.asyncio
async def test_analytics_overview_requires_auth(async_client, db_session, redis_mock):
    response = await async_client.get("/api/v1/admin/analytics/overview")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analytics_overview_with_auth(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.get(
        "/api/v1/admin/analytics/overview",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_page_views" in data
    assert "today_page_views" in data
    assert "total_posts" in data
    assert "total_comments" in data
    assert "yesterday_page_views" in data
    assert "total_drafts" in data
    assert "pending_comments" in data
    assert "growth_rate" in data
    assert "popular_posts" in data
    assert "page_views_daily" in data
    assert "comments_daily" in data
    assert "top_tags" in data


@pytest.mark.asyncio
async def test_analytics_trend_requires_auth(async_client, db_session, redis_mock):
    response = await async_client.get("/api/v1/admin/analytics/trend")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analytics_trend_with_auth(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.get(
        "/api/v1/admin/analytics/trend?metric=pv&days=7",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_analytics_trend_invalid_metric(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.get(
        "/api/v1/admin/analytics/trend?metric=invalid&days=7",
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analytics_trend_invalid_days(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.get(
        "/api/v1/admin/analytics/trend?metric=pv&days=0",
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_api_performance_requires_auth(async_client, db_session, redis_mock):
    response = await async_client.get("/api/v1/admin/analytics/api-performance")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_performance_with_auth(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.get(
        "/api/v1/admin/analytics/api-performance?hours=24",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_realtime_requires_auth(async_client, db_session, redis_mock):
    response = await async_client.get("/api/v1/admin/analytics/realtime")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_realtime_with_auth(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.get(
        "/api/v1/admin/analytics/realtime",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "online_users" in data
    assert "today_pv" in data
    assert "today_uv" in data
    assert "pv_per_minute" in data
