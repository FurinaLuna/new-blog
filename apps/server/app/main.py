from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import get_settings
from app.api.v1 import tags, posts, comments, auth, admin_posts, admin_media, admin_comments, ai, rss, analytics
from app.middleware.telemetry import TelemetryMiddleware
from app.utils.exceptions import AppError

settings = get_settings()

app = FastAPI(
    title="Personal Blog API",
    description="个人博客后端API，支持文章管理、评论、AI聊天等功能",
    version="1.0.0",
)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telemetry (must be before error handler to capture all requests)
app.add_middleware(TelemetryMiddleware)

# Unified error handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Static files for uploads
os.makedirs(settings.upload_dir, exist_ok=True)
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
app.include_router(rss.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
