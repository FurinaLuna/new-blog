from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tag import Tag
from app.repositories.tag_repository import TagRepository
from app.schemas.tag import TagCreate


async def get_all_tags(db: AsyncSession) -> list[Tag]:
    repo = TagRepository(db)
    return await repo.get_all_ordered()


async def get_tag_by_slug(db: AsyncSession, slug: str) -> Tag | None:
    repo = TagRepository(db)
    return await repo.get_by_slug(slug)


async def create_tag(db: AsyncSession, data: TagCreate) -> Tag:
    repo = TagRepository(db)
    return await repo.create(name=data.name, slug=data.slug)


async def get_or_create_tags(db: AsyncSession, names: list[dict]) -> list[Tag]:
    repo = TagRepository(db)
    tags = []
    for item in names:
        tag = await repo.get_by_slug(item["slug"])
        if not tag:
            tag = await repo.create(name=item["name"], slug=item["slug"])
        tags.append(tag)
    return tags
