import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_ai_chat(async_client, db_session, redis_mock):
    with patch("app.api.v1.ai.rag_chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = {"answer": "Test answer", "sources": []}
        response = await async_client.post(
            "/api/v1/ai/chat",
            json={"question": "What is AI?"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "session_id" in data


@pytest.mark.asyncio
async def test_ai_chat_with_session(async_client, db_session, redis_mock):
    with patch("app.api.v1.ai.rag_chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = {"answer": "Follow-up answer", "sources": []}
        response = await async_client.post(
            "/api/v1/ai/chat",
            json={"question": "Tell me more", "session_id": "test-session-123"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session-123"


@pytest.mark.asyncio
async def test_ai_chat_stream(async_client, db_session, redis_mock):
    async def mock_stream(*args, **kwargs):
        yield {"type": "token", "token": "Hello"}
        yield {"type": "token", "token": " world"}
        yield {"type": "sources", "sources": []}

    with patch("app.api.v1.ai.rag_chat_stream", side_effect=mock_stream):
        response = await async_client.post(
            "/api/v1/ai/chat/stream",
            json={"question": "What is AI?"},
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_ai_chat_with_sources(async_client, db_session, redis_mock):
    with patch("app.api.v1.ai.rag_chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = {
            "answer": "Based on the article...",
            "sources": [{"post_id": "p1", "post_title": "Test Post", "post_slug": "test-post", "chunk_text": "relevant text"}],
        }
        response = await async_client.post(
            "/api/v1/ai/chat",
            json={"question": "What does the article say?"},
        )
    assert response.status_code == 200
    data = response.json()
    assert len(data["sources"]) == 1
    assert data["sources"][0]["post_title"] == "Test Post"


@pytest.mark.asyncio
async def test_ai_chat_validation(async_client, db_session, redis_mock):
    response = await async_client.post(
        "/api/v1/ai/chat",
        json={},
    )
    assert response.status_code == 422
