from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.dependencies import get_current_user
from app.schemas.common import PaginatedResponse
from app.schemas.post import PostCreate, PostUpdate, PostListOut
from app.schemas.comment import BatchActionRequest
from app.schemas.analytics import AnalyticsOverview
from app.services import post_service as ps
from app.services import cache_service as cache
from app.services import analytics_service
from app.utils import build_paginated_response, NotFoundError, ConflictError

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/posts", response_model=PaginatedResponse)
async def admin_list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    result = await ps.get_post_list(db, page=page, size=size, search=search, admin=True)
    return build_paginated_response(result.items, result.total, result.page, result.size)


@router.post("/posts", response_model=PostListOut, status_code=status.HTTP_201_CREATED)
async def admin_create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _user: dict = Depends(get_current_user),
):
    existing = await ps.get_post_by_slug(db, data.slug)
    if existing:
        raise ConflictError("slug已存在")
    post = await ps.create_post(db, data, redis=redis)
    await cache.invalidate_post_caches(redis, post.slug)
    return PostListOut.model_validate(post)


@router.put("/posts/{post_id}", response_model=PostListOut)
async def admin_update_post(
    post_id: str,
    data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _user: dict = Depends(get_current_user),
):
    post = await ps.get_post_by_id(db, post_id)
    if not post:
        raise NotFoundError("文章不存在")
    if data.slug and data.slug != post.slug:
        existing = await ps.get_post_by_slug(db, data.slug)
        if existing:
            raise ConflictError("slug已存在")
    post = await ps.update_post(db, post, data, redis=redis)
    await cache.invalidate_post_caches(redis, post.slug)
    return PostListOut.model_validate(post)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _user: dict = Depends(get_current_user),
):
    post = await ps.get_post_by_id(db, post_id)
    if not post:
        raise NotFoundError("文章不存在")
    await ps.delete_post(db, post, redis=redis)
    await cache.invalidate_post_caches(redis, post.slug)


@router.post("/posts/{post_id}/reindex")
async def admin_reindex_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    from app.services.rag_service import index_post
    post = await ps.get_post_by_id(db, post_id)
    if not post:
        raise NotFoundError("文章不存在")
    count = await index_post(db, post.id, post.content)
    return {"indexed_chunks": count}


@router.post("/posts/batch-publish")
async def batch_publish_posts(
    data: BatchActionRequest,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    published = []
    failed = []
    for pid in data.ids:
        try:
            async with db.begin_nested():
                post = await ps.get_post_by_id(db, pid)
                if post:
                    post.published = True
                    await db.flush()
                    published.append(PostListOut.model_validate(post))
                else:
                    failed.append({"id": pid, "reason": "文章不存在"})
        except Exception:
            failed.append({"id": pid, "reason": "处理失败"})
    return {"published": published, "count": len(published), "failed": failed}


@router.post("/posts/batch-unpublish")
async def batch_unpublish_posts(
    data: BatchActionRequest,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    unpublished = []
    failed = []
    for pid in data.ids:
        try:
            async with db.begin_nested():
                post = await ps.get_post_by_id(db, pid)
                if post:
                    post.published = False
                    await db.flush()
                    unpublished.append(PostListOut.model_validate(post))
                else:
                    failed.append({"id": pid, "reason": "文章不存在"})
        except Exception:
            failed.append({"id": pid, "reason": "处理失败"})
    return {"unpublished": unpublished, "count": len(unpublished), "failed": failed}


@router.get("/analytics/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _user: dict = Depends(get_current_user),
):
    return await analytics_service.get_analytics_overview(db, redis)


@router.get("/analytics/posts")
async def get_analytics_post_stats(
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    return await analytics_service.get_post_stats(db)
