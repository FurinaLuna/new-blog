from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tag import Tag
from app.models.post import PostTag, Post
from app.schemas.tag import TagCreate


async def get_all_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.name))
    return list(result.scalars())


async def get_tag_by_slug(db: AsyncSession, slug: str) -> Tag | None:
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    return result.scalar_one_or_none()


async def create_tag(db: AsyncSession, data: TagCreate) -> Tag:
    tag = Tag(name=data.name, slug=data.slug)
    db.add(tag)
    await db.flush()
    return tag


async def get_or_create_tags(db: AsyncSession, names: list[dict]) -> list[Tag]:
    """Get or create tags from list of {name, slug} dicts."""
    tags = []
    for item in names:
        tag = await get_tag_by_slug(db, item["slug"])
        if not tag:
            tag = await create_tag(db, TagCreate(name=item["name"], slug=item["slug"]))
        tags.append(tag)
    return tags
