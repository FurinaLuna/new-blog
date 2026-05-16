from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment import Comment
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate


async def get_approved_comments(db: AsyncSession, post_id: str) -> list[Comment]:
    repo = CommentRepository(db)
    return await repo.get_approved_by_post(post_id)


async def get_pending_comments(db: AsyncSession, page: int = 1, size: int = 20) -> list[Comment]:
    repo = CommentRepository(db)
    return await repo.get_pending(page, size)


async def get_comments_by_status(db: AsyncSession, status: str | None = None, page: int = 1, size: int = 20) -> list[Comment]:
    repo = CommentRepository(db)
    comments = await repo.get_by_status(status, page, size)
    comments = await repo.get_with_post_title(comments)
    return comments


async def create_comment(db: AsyncSession, data: CommentCreate, ip_hash: str) -> Comment:
    repo = CommentRepository(db)
    return await repo.create(
        post_id=data.post_id,
        author=data.author,
        email=data.email,
        content=data.content,
        ip_hash=ip_hash,
        approved=False,
    )


async def create_reply(db: AsyncSession, parent: Comment, content: str, user: dict) -> Comment:
    repo = CommentRepository(db)
    return await repo.create(
        post_id=parent.post_id,
        author=user.get("username", "admin"),
        content=content,
        ip_hash="admin",
        approved=True,
        parent_id=parent.id,
    )


async def approve_comment(db: AsyncSession, comment: Comment) -> Comment:
    repo = CommentRepository(db)
    return await repo.update(comment, approved=True)


async def delete_comment(db: AsyncSession, comment: Comment) -> None:
    repo = CommentRepository(db)
    await repo.delete(comment)


async def get_comment_by_id(db: AsyncSession, comment_id: str) -> Comment | None:
    repo = CommentRepository(db)
    return await repo.get_by_id(comment_id)
