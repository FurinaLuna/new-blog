from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, text

from app.models.analytics import PageView, Event, ApiMetric
from app.models.post import Post


class AnalyticsRepository:
    def __init__(self, db):
        self.db = db

    async def record_page_view(
        self,
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
        self.db.add(pv)
        return pv

    async def record_events_batch(self, events: list[dict], ip_hash: str) -> list[Event]:
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
        self.db.add_all(records)
        return records

    async def record_api_metric(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
    ) -> ApiMetric:
        metric = ApiMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
        )
        self.db.add(metric)
        return metric

    async def get_overview_stats(self) -> dict:
        today = datetime.now(timezone.utc).date()

        total_pv = (await self.db.execute(select(func.count(PageView.id)))).scalar() or 0

        today_pv = (
            await self.db.execute(
                select(func.count(PageView.id)).where(func.date(PageView.created_at) == today)
            )
        ).scalar() or 0

        total_posts = (
            await self.db.execute(select(func.count(Post.id)).where(Post.published == True))
        ).scalar() or 0

        total_comments = (
            await self.db.execute(select(func.count()).select_from(text("comments")))
        ).scalar() or 0

        daily_query = (
            select(
                func.date(PageView.created_at).label("day"),
                func.count(PageView.id).label("count"),
            )
            .where(PageView.created_at >= today - timedelta(days=6))
            .group_by(text("day"))
            .order_by(text("day"))
        )
        daily_result = await self.db.execute(daily_query)
        pv_daily = [{"date": str(row.day), "count": row.count} for row in daily_result.all()]

        recent_result = await self.db.execute(
            select(Event).order_by(Event.created_at.desc()).limit(20)
        )
        recent_events = [
            {"event_type": e.event_type, "source_page": e.source_page, "created_at": e.created_at.isoformat()}
            for e in recent_result.scalars()
        ]

        return {
            "total_page_views": total_pv,
            "today_page_views": today_pv,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "page_views_daily": pv_daily,
            "recent_events": recent_events,
        }

    async def get_post_stats(self) -> list[dict]:
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
        result = await self.db.execute(query)
        return [{"title": r.title, "slug": r.slug, "view_count": r.view_count} for r in result.all()]
