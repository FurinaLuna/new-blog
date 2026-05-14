"""AI service layer — unified LLM interface (streaming + non-streaming) and embeddings."""

import json
from collections.abc import AsyncGenerator
from httpx import AsyncClient
from app.core.config import get_settings

settings = get_settings()


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }


def _embedding_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.embedding_api_key or settings.openai_api_key}",
        "Content-Type": "application/json",
    }


async def call_llm(messages: list[dict], temperature: float = 0.7, max_tokens: int = 1500) -> str:
    payload = {
        "model": settings.openai_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    async with AsyncClient(base_url=settings.openai_base_url, timeout=60.0) as client:
        response = await client.post("/chat/completions", headers=_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def call_llm_stream(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> AsyncGenerator[str, None]:
    payload = {
        "model": settings.openai_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    async with AsyncClient(base_url=settings.openai_base_url, timeout=120.0) as client:
        async with client.stream("POST", "/chat/completions", headers=_headers(), json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                line = line.strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue


async def summarize_post(title: str, content: str) -> str:
    """Generate a concise Chinese summary (50-80 chars) for a blog post."""
    excerpt = content[:3000]
    messages = [
        {
            "role": "system",
            "content": "You are a professional technical blog editor. Generate a concise summary in Chinese (50-80 characters). Output only the summary text, no prefixes.",
        },
        {
            "role": "user",
            "content": f"Title: {title}\n\nContent: {excerpt}",
        },
    ]
    return await call_llm(messages, temperature=0.3, max_tokens=200)


async def generate_embedding(text: str) -> list[float]:
    payload = {"model": settings.embedding_model, "input": text}
    base_url = settings.embedding_base_url or settings.openai_base_url
    async with AsyncClient(base_url=base_url, timeout=30.0) as client:
        response = await client.post("/embeddings", headers=_embedding_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]


async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    payload = {"model": settings.embedding_model, "input": texts}
    base_url = settings.embedding_base_url or settings.openai_base_url
    async with AsyncClient(base_url=base_url, timeout=60.0) as client:
        response = await client.post("/embeddings", headers=_embedding_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]
