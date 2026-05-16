import pytest


@pytest.mark.asyncio
async def test_list_tags(async_client, db_session, redis_mock, sample_tag):
    response = await async_client.get("/api/v1/tags")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_tag_admin(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.post(
        "/api/v1/admin/tags",
        json={"name": "NewTag", "slug": "new-tag"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "NewTag"
    assert data["slug"] == "new-tag"


@pytest.mark.asyncio
async def test_update_tag_admin(async_client, db_session, redis_mock, auth_headers, sample_tag):
    response = await async_client.put(
        f"/api/v1/admin/tags/{sample_tag.id}",
        json={"name": "UpdatedTag"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "UpdatedTag"


@pytest.mark.asyncio
async def test_delete_tag_admin(async_client, db_session, redis_mock, auth_headers, sample_tag):
    response = await async_client.delete(
        f"/api/v1/admin/tags/{sample_tag.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_tag_with_posts_fails(async_client, db_session, redis_mock, auth_headers, sample_tag, sample_post):
    from app.models.post import PostTag

    post_tag = PostTag(post_id=sample_post.id, tag_id=sample_tag.id)
    db_session.add(post_tag)
    await db_session.flush()

    response = await async_client.delete(
        f"/api/v1/admin/tags/{sample_tag.id}",
        headers=auth_headers,
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_admin_list_tags(async_client, db_session, redis_mock, auth_headers, sample_tag):
    response = await async_client.get("/api/v1/admin/tags", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_tag_duplicate_slug(async_client, db_session, redis_mock, auth_headers, sample_tag):
    response = await async_client.post(
        "/api/v1/admin/tags",
        json={"name": "AnotherTag", "slug": sample_tag.slug},
        headers=auth_headers,
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_tag_slug_conflict(async_client, db_session, redis_mock, auth_headers, sample_tag):
    from app.models.tag import Tag

    tag2 = Tag(id="test-tag-2", name="Tag2", slug="tag-2")
    db_session.add(tag2)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/admin/tags/{sample_tag.id}",
        json={"slug": "tag-2"},
        headers=auth_headers,
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_non_existent_tag(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.delete(
        "/api/v1/admin/tags/non-existent-id",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_tag_unauthorized(async_client, db_session, redis_mock):
    response = await async_client.post(
        "/api/v1/admin/tags",
        json={"name": "NoAuth", "slug": "no-auth"},
    )
    assert response.status_code == 401
