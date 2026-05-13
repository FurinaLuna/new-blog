from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.dependencies import get_client_ip
from app.schemas.analytics import AnalyticsEventIn
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


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

    # Update real-time counters in Redis
    for event in events:
        path = event.source_page
        await redis.incr(f"stats:pv:today:{path}")
        await redis.expire(f"stats:pv:today:{path}", 86400)

        if event.event_type == "post_read" and event.event_data:
            post_slug = event.event_data.get("post_slug", "")
            if post_slug:
                await redis.zincrby("stats:popular:posts", 1, post_slug)

    return {"received": len(events)}
