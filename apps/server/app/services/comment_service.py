from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment import Comment
from app.schemas.comment import CommentCreate


async def get_approved_comments(db: AsyncSession, post_id: str) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id, Comment.approved == True)
        .order_by(Comment.created_at.desc())
    )
    return list(result.scalars())


async def get_pending_comments(db: AsyncSession, page: int = 1, size: int = 20) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .where(Comment.approved == False)
        .order_by(Comment.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    return list(result.scalars())


async def create_comment(db: AsyncSession, data: CommentCreate, ip_hash: str) -> Comment:
    comment = Comment(
        post_id=data.post_id,
        author=data.author,
        email=data.email,
        content=data.content,
        approved=False,
    )
    db.add(comment)
    await db.flush()
    return comment


async def approve_comment(db: AsyncSession, comment: Comment) -> Comment:
    comment.approved = True
    db.add(comment)
    await db.flush()
    return comment


async def delete_comment(db: AsyncSession, comment: Comment) -> None:
    await db.delete(comment)


async def get_comment_by_id(db: AsyncSession, comment_id: str) -> Comment | None:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    return result.scalar_one_or_none()
