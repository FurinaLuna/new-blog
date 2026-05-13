"""Public tag endpoints — list tags, posts by tag."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.post import PaginatedResponse
from app.schemas.tag import TagOut
from app.services import tag_service
from app.services import post_service as ps
from app.utils import build_paginated_response, NotFoundError

router = APIRouter(tags=["tags"])


@router.get("", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    tags = await tag_service.get_all_tags(db)
    counts = await ps.get_tag_post_counts(db)
    return [
        TagOut(id=t.id, name=t.name, slug=t.slug, post_count=counts.get(t.id, 0))
        for t in tags
    ]


@router.get("/{slug}/posts", response_model=PaginatedResponse)
async def posts_by_tag(
    slug: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    tag = await tag_service.get_tag_by_slug(db, slug)
    if not tag:
        raise NotFoundError("标签不存在")
    result = await ps.get_post_list(db, page=page, size=size, tag=slug)
    return build_paginated_response(result.items, result.total, result.page, result.size)
