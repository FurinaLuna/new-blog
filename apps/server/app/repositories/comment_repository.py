from sqlalchemy import select

from app.models.comment import Comment
from app.models.post import Post
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

    async def get_by_status(self, status: str | None, page: int, size: int) -> list[Comment]:
        query = select(Comment)
        if status == "pending":
            query = query.where(Comment.approved == False)
        elif status == "approved":
            query = query.where(Comment.approved == True)
        query = query.order_by(Comment.created_at.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        return list(result.scalars())

    async def get_with_post_title(self, comments: list[Comment]) -> list[Comment]:
        if not comments:
            return comments
        post_ids = {c.post_id for c in comments}
        result = await self.db.execute(
            select(Post.id, Post.title).where(Post.id.in_(post_ids))
        )
        post_map = {row.id: row.title for row in result.all()}
        for c in comments:
            c.post_title = post_map.get(c.post_id)
        return comments
