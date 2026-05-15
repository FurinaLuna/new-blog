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


async def approve_comment(db: AsyncSession, comment: Comment) -> Comment:
    repo = CommentRepository(db)
    return await repo.update(comment, approved=True)


async def delete_comment(db: AsyncSession, comment: Comment) -> None:
    repo = CommentRepository(db)
    await repo.delete(comment)


async def get_comment_by_id(db: AsyncSession, comment_id: str) -> Comment | None:
    repo = CommentRepository(db)
    return await repo.get_by_id(comment_id)
