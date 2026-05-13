import uuid
import hashlib
from datetime import datetime, timezone, date, timedelta
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.models.analytics import PageView, Event, ApiMetric
from app.models.post import Post
from app.schemas.analytics import AnalyticsOverview


async def record_page_view(
    db: AsyncSession,
    path: str,
    referrer: str | None,
    user_agent: str | None,
    ip_hash: str,
    session_id: str,
) -> PageView:
    pv = PageView(
        path=path,
        referrer=referrer,
        user_agent=user_agent,
        ip_hash=ip_hash,
        session_id=session_id,
    )
    db.add(pv)
    return pv


async def record_events_batch(db: AsyncSession, events: list[dict], ip_hash: str) -> list[Event]:
    records = [
        Event(
            event_type=e["event_type"],
            event_data=e.get("event_data", {}),
            source_page=e["source_page"],
            session_id=e["session_id"],
            ip_hash=ip_hash,
        )
        for e in events
    ]
    db.add_all(records)
    return records


async def record_api_metric(
    db: AsyncSession,
    redis: Redis,
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
) -> None:
    metric = ApiMetric(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        duration_ms=duration_ms,
    )
    db.add(metric)


async def get_analytics_overview(db: AsyncSession, redis: Redis) -> AnalyticsOverview:
    today = datetime.now(timezone.utc).date()

    # Total page views
    total_pv = (await db.execute(select(func.count(PageView.id)))).scalar() or 0

    # Today page views
    today_pv = (
        await db.execute(
            select(func.count(PageView.id)).where(func.date(PageView.created_at) == today)
        )
    ).scalar() or 0

    # Total posts
    total_posts = (
        await db.execute(select(func.count(Post.id)).where(Post.published == True))
    ).scalar() or 0

    # Total comments
    total_comments = (
        await db.execute(select(func.count()).select_from(text("comments")))
    ).scalar() or 0

    # Popular posts from Redis
    popular = await redis.zrevrange("stats:popular:posts", 0, 4, withscores=True)
    popular_posts = []
    for post_slug, score in popular:
        popular_posts.append({"slug": post_slug.decode() if isinstance(post_slug, bytes) else post_slug, "views": int(score)})

    # Daily page views for last 7 days
    daily_query = (
        select(
            func.date(PageView.created_at).label("day"),
            func.count(PageView.id).label("count"),
        )
        .where(PageView.created_at >= today - timedelta(days=6))
        .group_by(text("day"))
        .order_by(text("day"))
    )
    daily_result = await db.execute(daily_query)
    pv_daily = [{"date": str(row.day), "count": row.count} for row in daily_result.all()]

    # Recent events
    recent_result = await db.execute(
        select(Event).order_by(Event.created_at.desc()).limit(20)
    )
    recent_events = [
        {"event_type": e.event_type, "source_page": e.source_page, "created_at": e.created_at.isoformat()}
        for e in recent_result.scalars()
    ]

    return AnalyticsOverview(
        total_page_views=total_pv,
        today_page_views=today_pv,
        total_posts=total_posts,
        total_comments=total_comments,
        popular_posts=popular_posts,
        page_views_daily=pv_daily,
        recent_events=recent_events,
    )


async def get_post_stats(db: AsyncSession) -> list[dict]:
    query = (
        select(
            Post.title,
            Post.slug,
            Post.view_count,
        )
        .where(Post.published == True)
        .order_by(Post.view_count.desc())
        .limit(20)
    )
    result = await db.execute(query)
    return [{"title": r.title, "slug": r.slug, "view_count": r.view_count} for r in result.all()]


def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:16]
