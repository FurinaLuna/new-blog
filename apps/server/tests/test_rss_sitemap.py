import pytest


@pytest.mark.asyncio
async def test_rss_feed(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get("/api/v1/rss")
    assert response.status_code == 200
    assert "application/rss+xml" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_rss_feed_contains_posts(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get("/api/v1/rss")
    content = response.text
    assert "Test Post" in content
    assert "test-post" in content


@pytest.mark.asyncio
async def test_rss_feed_cached(async_client, db_session, redis_mock, sample_post):
    response1 = await async_client.get("/api/v1/rss")
    assert response1.status_code == 200
    response2 = await async_client.get("/api/v1/rss")
    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_rss_feed_empty(async_client, db_session, redis_mock):
    response = await async_client.get("/api/v1/rss")
    assert response.status_code == 200
    assert "application/rss+xml" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_sitemap(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get("/sitemap.xml")
    assert response.status_code == 200
    assert "application/xml" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_sitemap_contains_posts(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get("/sitemap.xml")
    content = response.text
    assert "test-post" in content


@pytest.mark.asyncio
async def test_sitemap_cached(async_client, db_session, redis_mock, sample_post):
    response1 = await async_client.get("/sitemap.xml")
    assert response1.status_code == 200
    response2 = await async_client.get("/sitemap.xml")
    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_sitemap_empty(async_client, db_session, redis_mock):
    response = await async_client.get("/sitemap.xml")
    assert response.status_code == 200
