import json
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.redis import redis_client

METRICS_QUEUE_KEY = "queue:api_metrics"


class TelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        if not request.url.path.startswith("/api/v1/analytics"):
            try:
                metric = json.dumps({
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                })
                await redis_client.lpush(METRICS_QUEUE_KEY, metric)
            except Exception:
                pass

        return response


async def flush_metrics() -> int:
    from app.core.database import async_session
    from app.models.analytics import ApiMetric

    metrics = []
    for _ in range(100):
        data = await redis_client.rpop(METRICS_QUEUE_KEY)
        if data is None:
            break
        m = json.loads(data)
        metrics.append(ApiMetric(
            endpoint=m["endpoint"],
            method=m["method"],
            status_code=m["status_code"],
            duration_ms=m["duration_ms"],
        ))

    if not metrics:
        return 0

    try:
        async with async_session() as db:
            db.add_all(metrics)
            await db.commit()
    except Exception:
        pass

    return len(metrics)
