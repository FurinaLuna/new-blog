from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.dependencies import get_current_user
from app.schemas.tag import TagCreate, TagUpdate, TagAdminOut
from app.models.post import PostTag
from app.repositories.tag_repository import TagRepository
from app.services import tag_service
from app.services import post_service as ps
from app.utils import NotFoundError, ConflictError

router = APIRouter(prefix="/admin", tags=["admin-tags"])


@router.get("/tags", response_model=list[TagAdminOut])
async def admin_list_tags(
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    tags = await tag_service.get_all_tags(db)
    counts = await ps.get_tag_post_counts(db)
    return [
        TagAdminOut(id=t.id, name=t.name, slug=t.slug, post_count=counts.get(t.id, 0))
        for t in tags
    ]


@router.post("/tags", response_model=TagAdminOut, status_code=status.HTTP_201_CREATED)
async def admin_create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    existing = await tag_service.get_tag_by_slug(db, data.slug)
    if existing:
        raise ConflictError("slug已存在")
    tag = await tag_service.create_tag(db, data)
    return TagAdminOut(id=tag.id, name=tag.name, slug=tag.slug, post_count=0)


@router.put("/tags/{tag_id}", response_model=TagAdminOut)
async def admin_update_tag(
    tag_id: str,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    repo = TagRepository(db)
    tag = await repo.get_by_id(tag_id)
    if not tag:
        raise NotFoundError("标签不存在")
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未提供更新字段")
    if data.slug and data.slug != tag.slug:
        existing = await tag_service.get_tag_by_slug(db, data.slug)
        if existing:
            raise ConflictError("slug已存在")
    tag = await repo.update(tag, **update_data)
    counts = await ps.get_tag_post_counts(db)
    return TagAdminOut(id=tag.id, name=tag.name, slug=tag.slug, post_count=counts.get(tag.id, 0))


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    repo = TagRepository(db)
    tag = await repo.get_by_id(tag_id)
    if not tag:
        raise NotFoundError("标签不存在")
    result = await db.execute(
        select(func.count()).select_from(PostTag).where(PostTag.tag_id == tag_id)
    )
    post_count = result.scalar() or 0
    if post_count > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"该标签下有 {post_count} 篇关联文章，无法删除")
    await repo.delete(tag)
