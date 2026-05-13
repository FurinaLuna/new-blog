import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.database import async_session
from app.core.redis import redis_client
from app.services.analytics_service import record_api_metric


class TelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        # Skip telemetry for analytics events endpoint to avoid recursion
        if not request.url.path.startswith("/api/v1/analytics"):
            try:
                async with async_session() as db:
                    await record_api_metric(
                        db=db,
                        redis=redis_client,
                        endpoint=request.url.path,
                        method=request.method,
                        status_code=response.status_code,
                        duration_ms=round(duration_ms, 2),
                    )
            except Exception:
                pass  # Never let telemetry break the app

        return response
