import math
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.models.post import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreate, PostUpdate
from app.schemas.common import PaginatedResponse
from app.services import cache_service as cache
from app.utils.serializers import post_to_dict


def _paginated_to_dict(response: PaginatedResponse) -> dict:
    items = []
    for item in response.items:
        if isinstance(item, Post):
            items.append(post_to_dict(item))
        elif hasattr(item, "model_dump"):
            items.append(item.model_dump())
        else:
            items.append(item)
    return {
        "items": items,
        "total": response.total,
        "page": response.page,
        "size": response.size,
        "pages": response.pages,
    }


async def get_post_list(
    db: AsyncSession,
    redis: Redis | None = None,
    page: int = 1,
    size: int = 10,
    tag: str | None = None,
    search: str | None = None,
    admin: bool = False,
) -> PaginatedResponse:
    if redis and not admin and not search:
        cache_key = f"cache:posts:page:{page}:size:{size}:tag:{tag or 'none'}:search:none"
        cached = await cache.get_cached(redis, cache_key)
        if cached is not None:
            return PaginatedResponse(**cached)

    repo = PostRepository(db)
    posts, total = await repo.get_post_list(page=page, size=size, tag=tag, search=search, admin=admin)

    response = PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )

    if redis and not admin and not search:
        await cache.cache_post_list(redis, page, size, tag, None, _paginated_to_dict(response))

    if redis and search and not admin:
        cache_key = f"cache:posts:page:{page}:size:{size}:tag:none:search:{search}"
        serialized = cache._serialize(_paginated_to_dict(response))
        await redis.setex(cache_key, 300, serialized)

    return response


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    repo = PostRepository(db)
    return await repo.get_by_slug(slug)


async def get_post_by_id(db: AsyncSession, post_id: str) -> Post | None:
    repo = PostRepository(db)
    return await repo.get_by_id(post_id)


async def increment_view_count(db: AsyncSession, post: Post) -> None:
    repo = PostRepository(db)
    await repo.increment_view_count(post)


async def get_adjacent_posts(db: AsyncSession, post: Post, admin: bool = False) -> tuple[Post | None, Post | None]:
    repo = PostRepository(db)
    return await repo.get_adjacent_posts(post, admin=admin)


async def create_post(db: AsyncSession, data: PostCreate, redis: Redis | None = None) -> Post:
    repo = PostRepository(db)
    post = await repo.create(
        title=data.title,
        slug=data.slug,
        content=data.content,
        excerpt=data.excerpt,
        cover_image=data.cover_image,
        published=data.published,
        featured=data.featured,
    )
    if data.tag_ids:
        await repo.set_post_tags(post.id, data.tag_ids)

    post = await repo.get_by_id(post.id)

    if redis:
        await cache.invalidate_all_post_caches(redis)

    return post


async def update_post(db: AsyncSession, post: Post, data: PostUpdate, redis: Redis | None = None) -> Post:
    from datetime import datetime, timezone
    repo = PostRepository(db)
    update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
    update_data["updated_at"] = datetime.now(timezone.utc)
    post = await repo.update(post, **update_data)
    if data.tag_ids is not None:
        await repo.set_post_tags(post.id, data.tag_ids)

    post = await repo.get_by_id(post.id)

    if redis:
        await cache.invalidate_all_post_caches(redis)
        await cache.delete_cache(redis, f"cache:posts:detail:{post.slug}")

    return post


async def delete_post(db: AsyncSession, post: Post, redis: Redis | None = None) -> None:
    slug = post.slug
    repo = PostRepository(db)
    await repo.delete(post)

    if redis:
        await cache.invalidate_all_post_caches(redis)
        await cache.delete_cache(redis, f"cache:posts:detail:{slug}")


async def get_tag_post_counts(db: AsyncSession) -> dict:
    repo = PostRepository(db)
    return await repo.get_tag_post_counts()
