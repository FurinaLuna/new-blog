from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, LoginResponse
from app.models.user import User
from app.dependencies import get_client_ip
from app.services.analytics_service import hash_ip
from sqlalchemy import select

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    ip = await get_client_ip(request)
    ip_hash = hash_ip(ip)

    # Rate limit: max 5 login attempts per minute per IP
    key = f"rate:login:{ip_hash}"
    attempts = await redis.get(key)
    if attempts and int(attempts) >= 5:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="登录尝试过于频繁，请稍后再试")
    await redis.setex(key, 60, int(attempts or 0) + 1)

    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = create_access_token({"sub": user.id, "username": user.username})
    return LoginResponse(access_token=token)
