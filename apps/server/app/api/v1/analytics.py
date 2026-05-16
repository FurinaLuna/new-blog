from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.dependencies import get_client_ip, get_current_user
from app.schemas.analytics import AnalyticsEventIn, DailyStat, ApiPerformanceSummary, RealtimeStats
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

admin_router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


@router.post("/events", status_code=201)
async def receive_events(
    events: list[AnalyticsEventIn],
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    ip = await get_client_ip(request)
    ip_hash = analytics_service.hash_ip(ip)

    records = await analytics_service.record_events_batch(
        db,
        [e.model_dump() for e in events],
        ip_hash,
    )

    for event in events:
        path = event.source_page
        await redis.incr(f"stats:pv:today:{path}")
        await redis.expire(f"stats:pv:today:{path}", 86400)

        if event.event_type == "post_read" and event.event_data:
            post_slug = event.event_data.get("post_slug", "")
            if post_slug:
                await redis.zincrby("stats:popular:posts", 1, post_slug)

    return {"received": len(events)}


@admin_router.get("/trend", response_model=list[DailyStat])
async def get_trend(
    metric: str = Query("pv", regex="^(pv|comments)$"),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    return await analytics_service.get_trend(db, metric, days)


@admin_router.get("/api-performance", response_model=list[ApiPerformanceSummary])
async def get_api_performance(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    return await analytics_service.get_api_performance(db, hours)


@admin_router.get("/realtime", response_model=RealtimeStats)
async def get_realtime(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _user: dict = Depends(get_current_user),
):
    return await analytics_service.get_realtime_stats(db, redis)
