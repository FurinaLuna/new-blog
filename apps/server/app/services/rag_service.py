"""RAG pipeline — chunking, embedding, hybrid search, chat generation."""

from collections.abc import AsyncGenerator
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import PostEmbedding
from app.services.ai_service import generate_embedding, generate_embeddings_batch, call_llm, call_llm_stream

CHUNK_SIZE = 500  # characters per chunk

# Unified system prompt template
SYSTEM_PROMPT = """你是一个个人博客的AI助手。请根据以下博客文章内容回答用户的问题。
如果博客内容中没有相关信息，请如实告诉用户，不要编造。

博客相关内容：
{context}

请用中文回答，保持专业且友好的语气。回答末尾必须列出引用的文章标题（如果有的话）。"""


def split_text_into_chunks(text: str, max_chars: int = CHUNK_SIZE) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) <= max_chars:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks


async def index_post(db: AsyncSession, post_id: str, content: str) -> int:
    await db.execute(text("DELETE FROM post_embeddings WHERE post_id = :pid"), {"pid": post_id})
    chunks = split_text_into_chunks(content)
    if not chunks:
        return 0

    embeddings = await generate_embeddings_batch(chunks)
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        record = PostEmbedding(post_id=post_id, chunk_index=i, content=chunk)
        db.add(record)

    await db.flush()
    records = (
        await db.execute(
            select(PostEmbedding)
            .where(PostEmbedding.post_id == post_id)
            .order_by(PostEmbedding.chunk_index)
        )
    ).scalars().all()

    for record, emb in zip(records, embeddings):
        await db.execute(
            text("UPDATE post_embeddings SET embedding = :emb WHERE id = :id"),
            {"emb": str(emb), "id": record.id},
        )
    return len(chunks)


async def search_similar_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    query_embedding = await generate_embedding(query)
    emb_str = str(query_embedding)

    # 1. Vector search
    vector_result = await db.execute(
        text("""
            SELECT pe.id, pe.post_id, pe.chunk_index, pe.content,
                   1 - (pe.embedding <=> :emb::vector) AS similarity
            FROM post_embeddings pe
            JOIN posts p ON p.id = pe.post_id
            WHERE p.published = true
            ORDER BY pe.embedding <=> :emb::vector
            LIMIT 20
        """),
        {"emb": emb_str},
    )
    vector_rows = vector_result.all()

    # 2. Keyword search (pg_trgm)
    keyword_result = await db.execute(
        text("""
            SELECT pe.id, pe.post_id, pe.chunk_index, pe.content,
                   similarity(pe.content, :q) AS keyword_score
            FROM post_embeddings pe
            JOIN posts p ON p.id = pe.post_id
            WHERE p.published = true AND pe.content % :q
            ORDER BY keyword_score DESC
            LIMIT 20
        """),
        {"q": query},
    )
    keyword_rows = keyword_result.all()

    # 3. RRF fusion
    k = 60
    scores: dict[str, float] = {}
    docs: dict[str, dict] = {}

    for i, row in enumerate(vector_rows):
        scores[row.id] = scores.get(row.id, 0) + 1 / (k + i + 1)
        docs[row.id] = {"id": row.id, "post_id": row.post_id, "chunk_index": row.chunk_index, "content": row.content}

    for i, row in enumerate(keyword_rows):
        scores[row.id] = scores.get(row.id, 0) + 1 / (k + i + 1)
        if row.id not in docs:
            docs[row.id] = {"id": row.id, "post_id": row.post_id, "chunk_index": row.chunk_index, "content": row.content}

    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    seen_posts: set[str] = set()
    unique_results = []
    for doc_id in sorted_ids:
        res = docs[doc_id]
        if res["post_id"] not in seen_posts:
            seen_posts.add(res["post_id"])
            unique_results.append(res)
            if len(unique_results) >= top_k:
                break
    return unique_results


async def _build_context_and_sources(db: AsyncSession, chunks: list[dict]) -> tuple[str, list[dict]]:
    """Extract post metadata and build context + source list."""
    context_parts = []
    sources = []
    for chunk in chunks:
        post_result = await db.execute(
            text("SELECT id, title, slug FROM posts WHERE id = :pid"),
            {"pid": chunk["post_id"]},
        )
        post = post_result.fetchone()
        if post:
            context_parts.append(f"[来源: {post.title}]\n{chunk['content']}")
            sources.append({
                "post_id": str(post.id),
                "post_title": post.title,
                "post_slug": post.slug,
                "chunk_text": chunk["content"][:200],
            })

    context = "\n\n---\n\n".join(context_parts) if context_parts else "暂无相关文章内容。"
    return context, sources


# ——— Public API ———


async def rag_chat(
    db: AsyncSession,
    question: str,
    conversation_history: list[dict] | None = None,
) -> dict:
    """Non-streaming RAG chat with source citations."""
    chunks = await search_similar_chunks(db, question, top_k=5)
    context, sources = await _build_context_and_sources(db, chunks)

    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(context=context)}]
    if conversation_history:
        messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": question})

    answer = await call_llm(messages)
    return {"answer": answer, "sources": sources}


async def rag_chat_stream(
    db: AsyncSession,
    question: str,
    conversation_history: list[dict] | None = None,
) -> AsyncGenerator[dict, None]:
    """Streaming RAG chat — yields token events and a sources event."""
    chunks = await search_similar_chunks(db, question, top_k=5)
    context, sources = await _build_context_and_sources(db, chunks)

    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(context=context)}]
    if conversation_history:
        messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": question})

    # Yield sources first so the frontend can show citations immediately
    if sources:
        yield {"type": "sources", "sources": sources}

    async for token in call_llm_stream(messages):
        yield {"type": "token", "token": token}
