import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.redis import redis_client
from app.dependencies import get_client_ip

PATH_LIMITS = {
    "/api/v1/ai/chat": 10,
    "/api/v1/ai/chat/stream": 10,
    "/api/v1/auth/login": 5,
    "/api/v1/comments": 3,
}

DEFAULT_LIMIT = 60
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        limit = DEFAULT_LIMIT
        for prefix, cfg_limit in PATH_LIMITS.items():
            if path.startswith(prefix):
                limit = cfg_limit
                break

        if request.method == "OPTIONS":
            return await call_next(request)

        ip = await get_client_ip(request)
        key = f"rate_limit:{ip}:{path}"
        now = time.time()
        window_start = now - WINDOW_SECONDS

        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, WINDOW_SECONDS)
            results = await pipe.execute()
            count = results[2]

            if count > limit:
                retry_after = WINDOW_SECONDS
                return JSONResponse(
                    status_code=429,
                    content={"detail": "请求过于频繁，请稍后再试"},
                    headers={"Retry-After": str(retry_after)},
                )
        except Exception:
            pass

        response = await call_next(request)
        return response
