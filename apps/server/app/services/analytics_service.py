import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import AnalyticsOverview


async def record_page_view(
    db: AsyncSession,
    path: str,
    referrer: str | None,
    user_agent: str | None,
    ip_hash: str,
    session_id: str,
):
    repo = AnalyticsRepository(db)
    return await repo.record_page_view(path, referrer, user_agent, ip_hash, session_id)


async def record_events_batch(db: AsyncSession, events: list[dict], ip_hash: str):
    repo = AnalyticsRepository(db)
    return await repo.record_events_batch(events, ip_hash)


async def record_api_metric(
    db: AsyncSession,
    redis: Redis,
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
) -> None:
    repo = AnalyticsRepository(db)
    await repo.record_api_metric(endpoint, method, status_code, duration_ms)


async def get_analytics_overview(db: AsyncSession, redis: Redis) -> AnalyticsOverview:
    repo = AnalyticsRepository(db)
    stats = await repo.get_overview_stats()

    popular = await redis.zrevrange("stats:popular:posts", 0, 4, withscores=True)
    popular_posts = []
    for post_slug, score in popular:
        popular_posts.append({"slug": post_slug.decode() if isinstance(post_slug, bytes) else post_slug, "views": int(score)})

    return AnalyticsOverview(
        total_page_views=stats["total_page_views"],
        today_page_views=stats["today_page_views"],
        total_posts=stats["total_posts"],
        total_comments=stats["total_comments"],
        popular_posts=popular_posts,
        page_views_daily=stats["page_views_daily"],
        recent_events=stats["recent_events"],
    )


async def get_post_stats(db: AsyncSession) -> list[dict]:
    repo = AnalyticsRepository(db)
    return await repo.get_post_stats()


def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:16]
