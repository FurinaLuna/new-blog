import asyncio
import logging
import os
import shutil
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError

from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine, async_session
from app.core.logging import setup_logging
from app.core.redis import redis_client
from app.api.v1 import tags, posts, comments, auth, admin_posts, admin_media, admin_comments, admin_tags, ai, rss, analytics, sitemap
from app.middleware.telemetry import TelemetryMiddleware, flush_metrics
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.utils.exceptions import AppError

setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

_flush_task: asyncio.Task | None = None

_start_time: float = time.time()


async def _metrics_flush_loop():
    while True:
        try:
            await asyncio.sleep(5)
            await flush_metrics()
        except asyncio.CancelledError:
            try:
                await flush_metrics()
            except Exception:
                pass
            break
        except Exception:
            await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _flush_task
    logger.info("Starting up...")
    os.makedirs(settings.upload_dir, exist_ok=True)
    _flush_task = asyncio.create_task(_metrics_flush_loop())
    yield
    logger.info("Shutting down...")
    if _flush_task:
        _flush_task.cancel()
        try:
            await _flush_task
        except asyncio.CancelledError:
            pass
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(
    title="Personal Blog API",
    description="个人博客后端API，支持文章管理、评论、AI聊天等功能",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(GZipMiddleware, minimum_size=500)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.add_middleware(TelemetryMiddleware)

app.add_middleware(RateLimitMiddleware)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "detail": exc.detail, "code": exc.code},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    detail = "; ".join(
        f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors
    )
    return JSONResponse(
        status_code=422,
        content={"success": False, "detail": detail, "code": "VALIDATION_ERROR"},
    )


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "内部服务器错误", "code": "INTERNAL_ERROR"},
    )


app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

api_prefix = "/api/v1"
app.include_router(posts.router, prefix=f"{api_prefix}/posts")
app.include_router(tags.router, prefix=f"{api_prefix}/tags")
app.include_router(comments.router, prefix=f"{api_prefix}/comments")
app.include_router(auth.router, prefix=f"{api_prefix}/auth")
app.include_router(admin_posts.router, prefix=api_prefix)
app.include_router(admin_media.router, prefix=api_prefix)
app.include_router(admin_comments.router, prefix=api_prefix)
app.include_router(admin_tags.router, prefix=api_prefix)
app.include_router(ai.router, prefix=f"{api_prefix}/ai")
app.include_router(rss.router, prefix=f"{api_prefix}/rss")
app.include_router(analytics.router, prefix=api_prefix)
app.include_router(analytics.admin_router, prefix=api_prefix)
app.include_router(sitemap.router)


@app.get("/health")
async def health_check():
    checks = {}
    db_ok = False
    redis_ok = False

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"

    try:
        await redis_client.ping()
        redis_ok = True
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    disk_info = {}
    try:
        usage = shutil.disk_usage(settings.upload_dir)
        disk_info = {
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "used_gb": round(usage.used / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "percent": round(usage.used / usage.total * 100, 1),
        }
        disk_ok = usage.free > 100 * 1024 * 1024
        checks["disk"] = "ok" if disk_ok else "warning"
    except Exception:
        disk_ok = False
        checks["disk"] = "error"

    if db_ok and redis_ok and disk_ok:
        status = "ok"
    elif db_ok or redis_ok:
        status = "degraded"
    else:
        status = "unhealthy"

    uptime = int(time.time() - _start_time)

    result = {
        "status": status,
        "version": "1.0.0",
        "checks": checks,
        "uptime_seconds": uptime,
    }
    if disk_info:
        result["disk"] = disk_info

    return result


@app.get("/health/live")
async def liveness_probe():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness_probe():
    checks = {}

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"

    try:
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    ready = all(v == "ok" for v in checks.values())

    return {
        "status": "ready" if ready else "not_ready",
        "checks": checks,
    }
