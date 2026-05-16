import pytest


@pytest.mark.asyncio
async def test_get_comments(async_client, db_session, redis_mock, sample_post):
    response = await async_client.get(f"/api/v1/comments/{sample_post.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_comment(async_client, db_session, redis_mock, sample_post):
    response = await async_client.post(
        "/api/v1/comments",
        json={
            "post_id": sample_post.id,
            "author": "TestUser",
            "content": "Nice post!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["author"] == "TestUser"
    assert data["content"] == "Nice post!"


@pytest.mark.asyncio
async def test_create_comment_rate_limit(async_client, db_session, redis_mock, sample_post):
    for _ in range(3):
        await async_client.post(
            "/api/v1/comments",
            json={
                "post_id": sample_post.id,
                "author": "TestUser",
                "content": "Comment",
            },
        )
    response = await async_client.post(
        "/api/v1/comments",
        json={
            "post_id": sample_post.id,
            "author": "TestUser",
            "content": "One more",
        },
    )
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_approve_comment_admin(async_client, db_session, redis_mock, auth_headers, sample_post):
    from app.models.comment import Comment

    comment = Comment(
        id="test-comment-id",
        post_id=sample_post.id,
        author="TestUser",
        content="Test comment",
        approved=False,
    )
    db_session.add(comment)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/admin/comments/{comment.id}/approve",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == comment.id


@pytest.mark.asyncio
async def test_batch_approve_comments(async_client, db_session, redis_mock, auth_headers, sample_post):
    from app.models.comment import Comment

    comments = []
    for i in range(2):
        c = Comment(
            id=f"batch-comment-{i}",
            post_id=sample_post.id,
            author=f"User{i}",
            content=f"Comment {i}",
            approved=False,
        )
        db_session.add(c)
        comments.append(c)
    await db_session.flush()

    response = await async_client.post(
        "/api/v1/admin/comments/batch-approve",
        json={"ids": [c.id for c in comments]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2


@pytest.mark.asyncio
async def test_delete_comment_admin(async_client, db_session, redis_mock, auth_headers, sample_post):
    from app.models.comment import Comment

    comment = Comment(
        id="delete-comment-id",
        post_id=sample_post.id,
        author="DeleteUser",
        content="To be deleted",
        approved=False,
    )
    db_session.add(comment)
    await db_session.flush()

    response = await async_client.delete(
        f"/api/v1/admin/comments/{comment.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_batch_delete_comments(async_client, db_session, redis_mock, auth_headers, sample_post):
    from app.models.comment import Comment

    comments = []
    for i in range(3):
        c = Comment(
            id=f"batch-del-comment-{i}",
            post_id=sample_post.id,
            author=f"DelUser{i}",
            content=f"Delete comment {i}",
            approved=False,
        )
        db_session.add(c)
        comments.append(c)
    await db_session.flush()

    response = await async_client.post(
        "/api/v1/admin/comments/batch-delete",
        json={"ids": [c.id for c in comments]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"] == 3


@pytest.mark.asyncio
async def test_html_in_comment_stripped(async_client, db_session, redis_mock, sample_post):
    response = await async_client.post(
        "/api/v1/comments",
        json={
            "post_id": sample_post.id,
            "author": "HTMLUser",
            "content": "<b>Bold</b> <script>alert('xss')</script>text",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "<script>" not in data["content"]
    assert "<b>" not in data["content"]


@pytest.mark.asyncio
async def test_get_comments_by_status(async_client, db_session, redis_mock, auth_headers, sample_post):
    from app.models.comment import Comment

    comment = Comment(
        id="status-comment-id",
        post_id=sample_post.id,
        author="StatusUser",
        content="Status test",
        approved=False,
    )
    db_session.add(comment)
    await db_session.flush()

    response = await async_client.get(
        "/api/v1/admin/comments?status=pending",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_reply_comment(async_client, db_session, redis_mock, auth_headers, sample_post):
    from app.models.comment import Comment

    comment = Comment(
        id="reply-parent-id",
        post_id=sample_post.id,
        author="ParentUser",
        content="Parent comment",
        approved=True,
    )
    db_session.add(comment)
    await db_session.flush()

    response = await async_client.post(
        f"/api/v1/admin/comments/{comment.id}/reply",
        json={"content": "Admin reply content"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Admin reply content"
    assert data["author"] == "admin"


@pytest.mark.asyncio
async def test_reply_non_existent_comment(async_client, db_session, redis_mock, auth_headers):
    response = await async_client.post(
        "/api/v1/admin/comments/non-existent-id/reply",
        json={"content": "Reply to nothing"},
        headers=auth_headers,
    )
    assert response.status_code == 404
