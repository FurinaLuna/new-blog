from sqlalchemy import select, func

from app.models.media import Media
from app.repositories.base import BaseRepository


class MediaRepository(BaseRepository[Media]):
    def __init__(self, db):
        super().__init__(Media, db)

    async def get_paginated(self, page: int, size: int) -> tuple[list[Media], int]:
        total = (await self.db.execute(select(func.count(Media.id)))).scalar() or 0
        result = await self.db.execute(
            select(Media)
            .order_by(Media.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars()), total
