"""AI chat endpoints — RAG-powered non-streaming and streaming chat."""

import json
import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.ai import ChatRequest, ChatResponse, SourceCitation
from app.services.rag_service import rag_chat, rag_chat_stream

router = APIRouter(tags=["ai"])

# Conversation TTL: 1 hour
CONVERSATION_TTL = 3600
MAX_HISTORY = 20  # Keep last 10 exchanges


async def _get_history(redis: Redis, session_id: str) -> list[dict]:
    data = await redis.get(f"chat:history:{session_id}")
    return json.loads(data) if data else []


async def _save_history(redis: Redis, session_id: str, history: list[dict]):
    if history:
        await redis.setex(f"chat:history:{session_id}", CONVERSATION_TTL, json.dumps(history, ensure_ascii=False))


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    session_id = data.session_id or str(uuid.uuid4())
    history = await _get_history(redis, session_id)

    result = await rag_chat(db, data.question, conversation_history=history)

    # Save updated history
    history.append({"role": "user", "content": data.question})
    history.append({"role": "assistant", "content": result["answer"]})
    await _save_history(redis, session_id, history[-MAX_HISTORY:])

    return ChatResponse(
        answer=result["answer"],
        sources=[SourceCitation(**s) for s in result["sources"]],
        session_id=session_id,
    )


@router.post("/chat/stream")
async def ai_chat_stream(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    session_id = data.session_id or str(uuid.uuid4())
    history = await _get_history(redis, session_id)

    async def event_generator():
        full_answer = ""
        sources = []
        try:
            async for event in rag_chat_stream(db, data.question, conversation_history=history):
                if event.get("type") == "token":
                    full_answer += event["token"]
                    yield f"data: {json.dumps({'token': event['token']})}\n\n"
                elif event.get("type") == "sources":
                    sources = event["sources"]
                    yield f"data: {json.dumps({'sources': sources})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        # Save history after streaming completes
        history.append({"role": "user", "content": data.question})
        history.append({"role": "assistant", "content": full_answer})
        await _save_history(redis, session_id, history[-MAX_HISTORY:])

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Session-Id": session_id},
    )
