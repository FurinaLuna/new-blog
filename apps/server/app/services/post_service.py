import math
import hashlib
from datetime import datetime, timezone
from sqlalchemy import select, func, or_, desc, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.post import Post, PostTag
from app.schemas.post import PostCreate, PostUpdate, PaginatedResponse


async def get_post_list(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
    tag: str | None = None,
    search: str | None = None,
    admin: bool = False,
) -> PaginatedResponse:
    query = select(Post).options(selectinload(Post.tags).selectinload(PostTag.tag))

    if not admin:
        query = query.where(Post.published == True)

    if tag:
        query = query.join(Post.tags).join(PostTag.tag).where(PostTag.tag.has(slug=tag))

    if search:
        query = query.where(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%"),
                Post.excerpt.ilike(f"%{search}%"),
            )
        )

    query = query.order_by(desc(Post.created_at))

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar() or 0

    offset = (page - 1) * size
    result = await db.execute(query.offset(offset).limit(size))
    posts = list(result.scalars().unique())

    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    query = (
        select(Post)
        .options(selectinload(Post.tags).selectinload(PostTag.tag))
        .where(Post.slug == slug)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_post_by_id(db: AsyncSession, post_id: str) -> Post | None:
    query = (
        select(Post)
        .options(selectinload(Post.tags).selectinload(PostTag.tag))
        .where(Post.id == post_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def increment_view_count(db: AsyncSession, post: Post) -> None:
    post.view_count += 1
    db.add(post)


async def get_adjacent_posts(db: AsyncSession, post: Post, admin: bool = False) -> tuple[Post | None, Post | None]:
    base = select(Post)
    if not admin:
        base = base.where(Post.published == True)

    prev_query = base.where(Post.created_at < post.created_at).order_by(desc(Post.created_at)).limit(1)
    next_query = base.where(Post.created_at > post.created_at).order_by(Post.created_at).limit(1)

    prev_result = await db.execute(prev_query)
    next_result = await db.execute(next_query)
    return prev_result.scalar_one_or_none(), next_result.scalar_one_or_none()


async def create_post(db: AsyncSession, data: PostCreate) -> Post:
    post = Post(
        title=data.title,
        slug=data.slug,
        content=data.content,
        excerpt=data.excerpt,
        cover_image=data.cover_image,
        published=data.published,
        featured=data.featured,
    )
    db.add(post)
    await db.flush()

    if data.tag_ids:
        await _set_post_tags(db, post.id, data.tag_ids)

    return post


async def update_post(db: AsyncSession, post: Post, data: PostUpdate) -> Post:
    update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for key, value in update_data.items():
        setattr(post, key, value)
    post.updated_at = datetime.now(timezone.utc)
    db.add(post)
    await db.flush()

    if data.tag_ids is not None:
        await _set_post_tags(db, post.id, data.tag_ids)

    return post


async def delete_post(db: AsyncSession, post: Post) -> None:
    await db.delete(post)


async def _set_post_tags(db: AsyncSession, post_id: str, tag_ids: list[str]) -> None:
    await db.execute(text("DELETE FROM post_tags WHERE post_id = :pid"), {"pid": post_id})
    for tag_id in tag_ids:
        db.add(PostTag(post_id=post_id, tag_id=tag_id))


async def get_tag_post_counts(db: AsyncSession) -> dict:
    query = (
        select(PostTag.tag_id, func.count(PostTag.post_id).label("count"))
        .join(Post, Post.id == PostTag.post_id)
        .where(Post.published == True)
        .group_by(PostTag.tag_id)
    )
    result = await db.execute(query)
    return {row.tag_id: row.count for row in result.all()}
