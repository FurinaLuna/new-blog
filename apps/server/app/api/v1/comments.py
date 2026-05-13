from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.dependencies import get_client_ip
from app.schemas.comment import CommentCreate, CommentOut
from app.services import comment_service
from app.services.analytics_service import hash_ip

router = APIRouter(tags=["comments"])


@router.get("/{post_id}", response_model=list[CommentOut])
async def get_comments(post_id: str, db: AsyncSession = Depends(get_db)):
    comments = await comment_service.get_approved_comments(db, post_id)
    return [CommentOut.model_validate(c) for c in comments]


@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    ip = await get_client_ip(request)
    ip_hash = hash_ip(ip)

    # Rate limit: max 3 comments per minute per IP
    key = f"rate:comment:{ip_hash}"
    count = await redis.get(key)
    if count and int(count) >= 3:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="评论过于频繁，请稍后再试")
    await redis.setex(key, 60, int(count or 0) + 1)

    comment = await comment_service.create_comment(db, data, ip_hash)
    return CommentOut.model_validate(comment)
