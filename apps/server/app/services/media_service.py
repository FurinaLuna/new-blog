import hashlib
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.models.media import Media
from app.core.config import get_settings

settings = get_settings()


async def save_media(
    db: AsyncSession,
    filename: str,
    file_path: str,
    mime_type: str,
    size: int,
) -> Media:
    url = f"/uploads/{filename}"
    media = Media(
        filename=filename,
        file_path=file_path.replace("\\", "/"),
        url=url,
        mime_type=mime_type,
        size=size,
    )
    db.add(media)
    await db.flush()
    return media


async def get_all_media(db: AsyncSession, page: int = 1, size: int = 20):
    from sqlalchemy import select, func
    total = (await db.execute(select(func.count(Media.id)))).scalar() or 0
    result = await db.execute(
        select(Media)
        .order_by(Media.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    return list(result.scalars()), total


async def get_media_by_id(db: AsyncSession, media_id: str) -> Media | None:
    from sqlalchemy import select
    result = await db.execute(select(Media).where(Media.id == media_id))
    return result.scalar_one_or_none()


async def delete_media(db: AsyncSession, media: Media) -> None:
    await db.delete(media)
