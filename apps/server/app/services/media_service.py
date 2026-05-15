from sqlalchemy.ext.asyncio import AsyncSession
from app.models.media import Media
from app.repositories.media_repository import MediaRepository
from app.core.config import get_settings

settings = get_settings()


async def save_media(
    db: AsyncSession,
    filename: str,
    file_path: str,
    mime_type: str,
    size: int,
) -> Media:
    repo = MediaRepository(db)
    url = f"/uploads/{filename}"
    return await repo.create(
        filename=filename,
        file_path=file_path.replace("\\", "/"),
        url=url,
        mime_type=mime_type,
        size=size,
    )


async def get_all_media(db: AsyncSession, page: int = 1, size: int = 20):
    repo = MediaRepository(db)
    return await repo.get_paginated(page, size)


async def get_media_by_id(db: AsyncSession, media_id: str) -> Media | None:
    repo = MediaRepository(db)
    return await repo.get_by_id(media_id)


async def delete_media(db: AsyncSession, media: Media) -> None:
    repo = MediaRepository(db)
    await repo.delete(media)
