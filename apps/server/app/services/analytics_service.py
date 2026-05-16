import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import AnalyticsOverview, GrowthRate, RealtimeStats, DailyStat, PopularPost, TopTag, ApiPerformanceSummary


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
        slug_str = post_slug.decode() if isinstance(post_slug, bytes) else post_slug
        popular_posts.append(PopularPost(slug=slug_str, title=slug_str, views=int(score)))

    yesterday_pv = await repo.get_yesterday_page_views()
    total_drafts = await repo.get_total_drafts()
    pending_comments = await repo.get_pending_comments_count()
    comments_daily = await repo.get_comments_daily()
    top_tags_raw = await repo.get_top_tags()
    top_tags = [TopTag(**t) for t in top_tags_raw]

    growth_rate = await get_growth_rate(db)

    return AnalyticsOverview(
        total_page_views=stats["total_page_views"],
        today_page_views=stats["today_page_views"],
        yesterday_page_views=yesterday_pv,
        total_posts=stats["total_posts"],
        total_comments=stats["total_comments"],
        total_drafts=total_drafts,
        pending_comments=pending_comments,
        growth_rate=growth_rate,
        popular_posts=popular_posts,
        page_views_daily=[DailyStat(**d) for d in stats["page_views_daily"]],
        comments_daily=[DailyStat(**d) for d in comments_daily],
        top_tags=top_tags,
        recent_events=stats["recent_events"],
    )


async def get_post_stats(db: AsyncSession) -> list[dict]:
    repo = AnalyticsRepository(db)
    return await repo.get_post_stats()


async def get_growth_rate(db: AsyncSession) -> GrowthRate:
    repo = AnalyticsRepository(db)

    today_pv = await repo.get_overview_stats()
    today_pv_count = today_pv["today_page_views"]
    yesterday_pv = await repo.get_yesterday_page_views()

    today_comments = await repo.get_today_comments_count()
    yesterday_comments = await repo.get_yesterday_comments_count()

    today_posts = await repo.get_today_posts_count()
    yesterday_posts = await repo.get_yesterday_posts_count()

    def calc_rate(today_val: int, yesterday_val: int) -> float:
        if yesterday_val == 0:
            return 0.0 if today_val == 0 else 100.0
        return round((today_val - yesterday_val) / yesterday_val * 100, 2)

    return GrowthRate(
        pv=calc_rate(today_pv_count, yesterday_pv),
        comments=calc_rate(today_comments, yesterday_comments),
        posts=calc_rate(today_posts, yesterday_posts),
    )


async def get_api_performance(db: AsyncSession, hours: int = 24) -> list[ApiPerformanceSummary]:
    repo = AnalyticsRepository(db)
    raw = await repo.get_api_performance_summary(hours)
    return [ApiPerformanceSummary(**r) for r in raw]


async def get_realtime_stats(db: AsyncSession, redis: Redis) -> RealtimeStats:
    repo = AnalyticsRepository(db)

    online_users = await redis.get("stats:online_users")
    online_users_count = int(online_users) if online_users else 0

    today_pv = await repo.get_overview_stats()
    today_pv_count = today_pv["today_page_views"]

    today_uv = await repo.get_uv_count(days=1)
    pv_per_minute = await repo.get_pv_per_minute()

    return RealtimeStats(
        online_users=online_users_count,
        today_pv=today_pv_count,
        today_uv=today_uv,
        pv_per_minute=pv_per_minute,
    )


async def get_trend(db: AsyncSession, metric: str, days: int = 7) -> list[DailyStat]:
    repo = AnalyticsRepository(db)
    raw = await repo.get_trend_daily(metric, days)
    return [DailyStat(**d) for d in raw]


def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:16]
