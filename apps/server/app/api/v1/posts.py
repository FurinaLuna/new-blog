from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import get_settings
from app.schemas.common import PaginatedResponse
from app.schemas.post import PostDetailOut, PostListOut
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
    redis: Redis = Depends(get_redis),
):
    result = await ps.get_post_list(db, redis=redis, page=page, size=size, tag=tag)
    return build_paginated_response(result.items, result.total, result.page, result.size)


@router.get("/search", response_model=PaginatedResponse)
async def search_posts(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    result = await ps.get_post_list(db, redis=redis, page=page, size=size, search=q)
    return build_paginated_response(result.items, result.total, result.page, result.size)


@router.get("/{slug}", response_model=PostDetailOut)
async def get_post_detail(
    slug: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    cache_key = f"cache:posts:detail:{slug}"
    cached = await cache.get_cached(redis, cache_key)
    if cached is not None:
        try:
            return PostDetailOut(**cached)
        except Exception:
            await cache.delete_cache(redis, cache_key)

    post = await ps.get_post_by_slug(db, slug)
    if not post or not post.published:
        raise NotFoundError("文章不存在")

    prev_post, next_post = await ps.get_adjacent_posts(db, post)

    await ps.increment_view_count(db, post)
    await cache.add_to_sorted_set(redis, "stats:popular:posts", post.slug)

    tags = [{"id": pt.tag.id, "name": pt.tag.name, "slug": pt.tag.slug} for pt in post.tags]
    result = PostDetailOut(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        excerpt=post.excerpt,
        cover_image=post.cover_image,
        featured=post.featured,
        view_count=post.view_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        tags=tags,
        prev_post=PostListOut.model_validate(prev_post) if prev_post else None,
        next_post=PostListOut.model_validate(next_post) if next_post else None,
    )

    await cache.cache_post_detail(redis, slug, result)
    return result


@router.get("/{slug}/summary")
async def get_post_summary(
    slug: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    cache_key = f"post:summary:{slug}"

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
