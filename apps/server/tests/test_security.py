import pytest


@pytest.mark.asyncio
async def test_security_headers_present(async_client, db_session, redis_mock):
    response = await async_client.get("/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("x-xss-protection") == "1; mode=block"
    assert "referrer-policy" in response.headers
    assert "content-security-policy" in response.headers


@pytest.mark.asyncio
async def test_rate_limit_middleware(async_client, db_session, redis_mock):
    for _ in range(65):
        await async_client.get("/api/v1/posts")
    response = await async_client.get("/api/v1/posts")
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_sql_injection_prevention(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get("/api/v1/posts/search?q=' OR 1=1 --")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_xss_prevention(async_client, db_session, redis_mock, sample_post):
    response = await async_client.post(
        "/api/v1/comments",
        json={
            "post_id": sample_post.id,
            "author": "Hacker",
            "content": "<script>alert('xss')</script>Hello",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "<script>" not in data["content"]


@pytest.mark.asyncio
async def test_upload_svg_blocked(async_client, db_session, redis_mock, auth_headers):
    import io

    svg_file = io.BytesIO(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    response = await async_client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.svg", svg_file, "image/svg+xml")},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_path_traversal_blocked(async_client, db_session, redis_mock, auth_headers):
    import io

    png_file = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    response = await async_client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("../../../etc/passwd.png", png_file, "image/png")},
        headers=auth_headers,
    )
    assert response.status_code in (400, 422)
