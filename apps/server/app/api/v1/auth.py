from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import verify_password, hash_password, create_access_token, create_refresh_token, decode_access_token, decode_refresh_token, blacklist_token, is_token_blacklisted
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, ChangePasswordRequest, LogoutRequest
from app.models.user import User
from app.dependencies import get_current_user, get_client_ip
from app.services.analytics_service import hash_ip
from sqlalchemy import select

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    ip = await get_client_ip(request)
    ip_hash = hash_ip(ip)

    key = f"rate:login:{ip_hash}"
    attempts = await redis.get(key)
    if attempts and int(attempts) >= 5:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="登录尝试过于频繁，请稍后再试")
    await redis.setex(key, 60, int(attempts or 0) + 1)

    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token_data = {"sub": user.id, "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(
    request: Request,
    body: LogoutRequest = LogoutRequest(),
    user: dict = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    if token:
        payload = decode_access_token(token)
        if payload:
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                await blacklist_token(jti, exp, redis)

    if body.refresh_token:
        refresh_payload = decode_refresh_token(body.refresh_token)
        if refresh_payload:
            rjti = refresh_payload.get("jti")
            rexp = refresh_payload.get("exp")
            if rjti and rexp:
                await blacklist_token(rjti, rexp, redis)

    return {"detail": "已成功登出"}


@router.post("/refresh", response_model=LoginResponse)
async def refresh(data: RefreshRequest, redis: Redis = Depends(get_redis)):
    payload = decode_refresh_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌无效或已过期")

    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti, redis):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌已被撤销")

    if jti and payload.get("exp"):
        await blacklist_token(jti, payload["exp"], redis)

    token_data = {"sub": payload.get("sub"), "username": payload.get("username")}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    user_id = user.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if not verify_password(data.old_password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
    db_user.password_hash = hash_password(data.new_password)
    db.add(db_user)
    await db.flush()
    return {"detail": "密码修改成功"}
