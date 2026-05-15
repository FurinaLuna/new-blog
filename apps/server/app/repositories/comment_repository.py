from sqlalchemy import select

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db):
        super().__init__(Comment, db)

    async def get_approved_by_post(self, post_id: str) -> list[Comment]:
        result = await self.db.execute(
            select(Comment)
            .where(Comment.post_id == post_id, Comment.approved == True)
            .order_by(Comment.created_at.desc())
        )
        return list(result.scalars())

    async def get_pending(self, page: int, size: int) -> list[Comment]:
        result = await self.db.execute(
            select(Comment)
            .where(Comment.approved == False)
            .order_by(Comment.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars())
