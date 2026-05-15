import re
import math
from sqlalchemy import select, func, or_, desc, text
from sqlalchemy.orm import selectinload

from app.models.post import Post, PostTag
from app.repositories.base import BaseRepository


def _is_chinese(s: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", s))


class PostRepository(BaseRepository[Post]):
    def __init__(self, db):
        super().__init__(Post, db)

    async def get_post_list(
        self,
        page: int,
        size: int,
        tag: str | None = None,
        search: str | None = None,
        admin: bool = False,
    ) -> tuple[list[Post], int]:
        query = select(Post).options(selectinload(Post.tags).selectinload(PostTag.tag))

        if not admin:
            query = query.where(Post.published == True)

        if tag:
            query = query.join(Post.tags).join(PostTag.tag).where(PostTag.tag.has(slug=tag))

        if search:
            if _is_chinese(search):
                query = query.where(
                    or_(
                        Post.title.ilike(f"%{search}%"),
                        Post.content.ilike(f"%{search}%"),
                        Post.excerpt.ilike(f"%{search}%"),
                    )
                )
            else:
                ts_query = " & ".join(search.split())
                query = query.where(
                    or_(
                        text("to_tsvector('english', posts.title) @@ to_tsquery('english', :q)"),
                        text("to_tsvector('english', posts.content) @@ to_tsquery('english', :q)"),
                        Post.title.ilike(f"%{search}%"),
                        Post.excerpt.ilike(f"%{search}%"),
                    )
                ).params(q=ts_query)

        query = query.order_by(desc(Post.created_at))

        total_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(total_query)).scalar() or 0

        offset = (page - 1) * size
        result = await self.db.execute(query.offset(offset).limit(size))
        posts = list(result.scalars().unique())

        return posts, total

    async def get_by_slug(self, slug: str) -> Post | None:
        query = (
            select(Post)
            .options(selectinload(Post.tags).selectinload(PostTag.tag))
            .where(Post.slug == slug)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_adjacent_posts(self, post: Post, admin: bool = False) -> tuple[Post | None, Post | None]:
        base = select(Post)
        if not admin:
            base = base.where(Post.published == True)

        prev_query = base.where(Post.created_at < post.created_at).order_by(desc(Post.created_at)).limit(1)
        next_query = base.where(Post.created_at > post.created_at).order_by(Post.created_at).limit(1)

        prev_result = await self.db.execute(prev_query)
        next_result = await self.db.execute(next_query)
        return prev_result.scalar_one_or_none(), next_result.scalar_one_or_none()

    async def increment_view_count(self, post: Post) -> None:
        await self.db.execute(
            text("UPDATE posts SET view_count = view_count + 1 WHERE id = :id"),
            {"id": post.id},
        )

    async def set_post_tags(self, post_id: str, tag_ids: list[str]) -> None:
        await self.db.execute(text("DELETE FROM post_tags WHERE post_id = :pid"), {"pid": post_id})
        for tag_id in tag_ids:
            self.db.add(PostTag(post_id=post_id, tag_id=tag_id))
        await self.db.flush()

    async def get_tag_post_counts(self) -> dict:
        query = (
            select(PostTag.tag_id, func.count(PostTag.post_id).label("count"))
            .join(Post, Post.id == PostTag.post_id)
            .where(Post.published == True)
            .group_by(PostTag.tag_id)
        )
        result = await self.db.execute(query)
        return {row.tag_id: row.count for row in result.all()}

    async def get_by_id(self, id: str) -> Post | None:
        query = (
            select(Post)
            .options(selectinload(Post.tags).selectinload(PostTag.tag))
            .where(Post.id == id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
