import pytest


@pytest.mark.asyncio
async def test_list_posts(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get("/api/v1/posts")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_list_posts_pagination(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get("/api/v1/posts?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 5


@pytest.mark.asyncio
async def test_search_posts(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get("/api/v1/posts/search?q=Test")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_get_post_detail(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get(f"/api/v1/posts/{sample_post.slug}")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == sample_post.slug
    assert data["title"] == sample_post.title


@pytest.mark.asyncio
async def test_get_post_summary(async_client, db_session, redis_mock, sample_post):
    with pytest.MonkeyPatch.context() as m:
        from app.services import ai_service

        async def fake_summarize(title, content):
            return "Fake summary"

        m.setattr(ai_service, "summarize_post", fake_summarize)
        response = await async_client.get(f"/api/v1/posts/{sample_post.slug}/summary")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data


@pytest.mark.asyncio
async def test_create_post_admin(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.post(
        "/api/v1/admin/posts",
        json={
            "title": "New Post",
            "slug": "new-post",
            "content": "This is new post content that is long enough.",
            "published": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "new-post"


@pytest.mark.asyncio
async def test_update_post_admin(async_client, db_session, redis_mock, auth_headers, sample_post):
    response = await async_client.put(
        f"/api/v1/admin/posts/{sample_post.id}",
        json={"title": "Updated Title"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_post_admin(async_client, db_session, redis_mock, auth_headers, sample_post):
    response = await async_client.delete(
        f"/api/v1/admin/posts/{sample_post.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_post_unauthorized(async_client, db_session, redis_mock):
    response = await async_client.post(
        "/api/v1/admin/posts",
        json={
            "title": "Unauthorized Post",
            "slug": "unauthorized-post",
            "content": "Should not be created.",
        },
    )
    assert response.status_code == 401
