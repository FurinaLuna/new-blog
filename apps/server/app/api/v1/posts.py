"""Public post endpoints — list, search, detail, and AI summary."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import get_settings
from app.schemas.post import PostDetailOut, PaginatedResponse
from app.services import post_service as ps
from app.services import cache_service as cache
from app.services import ai_service
from app.utils import build_paginated_response, NotFoundError

router = APIRouter(tags=["posts"])
settings = get_settings()


@router.get("", response_model=PaginatedResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await ps.get_post_list(db, page=page, size=size, tag=tag)
    return build_paginated_response(result.items, result.total, result.page, result.size)


@router.get("/search", response_model=PaginatedResponse)
async def search_posts(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await ps.get_post_list(db, page=page, size=size, search=q)
    return build_paginated_response(result.items, result.total, result.page, result.size)


@router.get("/{slug}", response_model=PostDetailOut)
async def get_post_detail(
    slug: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    post = await ps.get_post_by_slug(db, slug)
    if not post or not post.published:
        raise NotFoundError("文章不存在")

    # Increment view count (DB write) + update Redis sorted set
    await ps.increment_view_count(db, post)
    await cache.add_to_sorted_set(redis, "stats:popular:posts", post.slug)

    prev_post, next_post = await ps.get_adjacent_posts(db, post)

    from app.schemas.post import PostListOut
    tags = [{"id": pt.tag.id, "name": pt.tag.name, "slug": pt.tag.slug} for pt in post.tags]
    return PostDetailOut(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        excerpt=post.excerpt,
        cover_image=post.cover_image,
        featured=post.featured,
        view_count=post.view_count,  # already incremented
        created_at=post.created_at,
        updated_at=post.updated_at,
        tags=tags,
        prev_post=PostListOut.model_validate(prev_post) if prev_post else None,
        next_post=PostListOut.model_validate(next_post) if next_post else None,
    )


@router.get("/{slug}/summary")
async def get_post_summary(
    slug: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Get AI-generated summary for a post. Cached in Redis for 7 days."""
    cache_key = f"post:summary:{slug}"

    # Check cache first
    cached = await cache.get_cached(redis, cache_key)
    if cached:
        return cached

    post = await ps.get_post_by_slug(db, slug)
    if not post or not post.published:
        raise NotFoundError("文章不存在")

    summary = await ai_service.summarize_post(post.title, post.content)
    result = {"slug": slug, "summary": summary}
    await cache.set_cache(redis, cache_key, result, ttl=604800)
    return result
