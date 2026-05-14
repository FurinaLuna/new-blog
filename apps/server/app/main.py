import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import os

from app.core.config import get_settings
from app.core.database import engine, async_session
from app.core.redis import redis_client
from app.api.v1 import tags, posts, comments, auth, admin_posts, admin_media, admin_comments, ai, rss, analytics
from app.middleware.telemetry import TelemetryMiddleware
from app.utils.exceptions import AppError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    os.makedirs(settings.upload_dir, exist_ok=True)
    yield
    logger.info("Shutting down...")
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(
    title="Personal Blog API",
    description="个人博客后端API，支持文章管理、评论、AI聊天等功能",
    version="1.0.0",
    lifespan=lifespan,
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Telemetry
app.add_middleware(TelemetryMiddleware)

# Unified error handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# API v1 routes
api_prefix = "/api/v1"
app.include_router(posts.router, prefix=f"{api_prefix}/posts")
app.include_router(tags.router, prefix=f"{api_prefix}/tags")
app.include_router(comments.router, prefix=f"{api_prefix}/comments")
app.include_router(auth.router, prefix=f"{api_prefix}/auth")
app.include_router(admin_posts.router, prefix=api_prefix)
app.include_router(admin_media.router, prefix=api_prefix)
app.include_router(admin_comments.router, prefix=api_prefix)
app.include_router(ai.router, prefix=f"{api_prefix}/ai")
app.include_router(rss.router, prefix=f"{api_prefix}/rss")
app.include_router(analytics.router, prefix=api_prefix)


@app.get("/health")
async def health_check():
    try:
        await redis_client.ping()
    except Exception:
        return {"status": "degraded", "redis": "unreachable"}
    try:
        from sqlalchemy import text
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        return {"status": "degraded", "database": "unreachable"}
    return {"status": "ok"}
