from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, text, case

from app.models.analytics import PageView, Event, ApiMetric
from app.models.post import Post, PostTag
from app.models.comment import Comment
from app.models.tag import Tag


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

    async def get_yesterday_page_views(self) -> int:
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        result = (
            await self.db.execute(
                select(func.count(PageView.id)).where(func.date(PageView.created_at) == yesterday)
            )
        ).scalar() or 0
        return result

    async def get_total_drafts(self) -> int:
        result = (
            await self.db.execute(select(func.count(Post.id)).where(Post.published == False))
        ).scalar() or 0
        return result

    async def get_pending_comments_count(self) -> int:
        result = (
            await self.db.execute(select(func.count(Comment.id)).where(Comment.approved == False))
        ).scalar() or 0
        return result

    async def get_comments_daily(self, days: int = 7) -> list[dict]:
        today = datetime.now(timezone.utc).date()
        query = (
            select(
                func.date(Comment.created_at).label("day"),
                func.count(Comment.id).label("count"),
            )
            .where(Comment.created_at >= today - timedelta(days=days - 1))
            .group_by(text("day"))
            .order_by(text("day"))
        )
        result = await self.db.execute(query)
        return [{"date": str(row.day), "count": row.count} for row in result.all()]

    async def get_top_tags(self, limit: int = 10) -> list[dict]:
        query = (
            select(
                Tag.name,
                Tag.slug,
                func.count(PostTag.post_id).label("post_count"),
            )
            .join(PostTag, Tag.id == PostTag.tag_id)
            .group_by(Tag.id, Tag.name, Tag.slug)
            .order_by(text("post_count desc"))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return [{"name": row.name, "slug": row.slug, "post_count": row.post_count} for row in result.all()]

    async def get_api_performance_summary(self, hours: int = 24) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = (
            select(
                ApiMetric.endpoint,
                ApiMetric.method,
                func.avg(ApiMetric.duration_ms).label("avg_duration_ms"),
                func.count(ApiMetric.id).label("request_count"),
                func.sum(case((ApiMetric.status_code >= 400, 1), else_=0)).label("error_count"),
            )
            .where(ApiMetric.created_at >= since)
            .group_by(ApiMetric.endpoint, ApiMetric.method)
            .order_by(text("request_count desc"))
        )
        result = await self.db.execute(query)
        rows = result.all()

        summaries = []
        for row in rows:
            request_count = row.request_count
            error_count = row.error_count or 0
            p95_result = await self.db.execute(
                select(ApiMetric.duration_ms)
                .where(ApiMetric.endpoint == row.endpoint, ApiMetric.method == row.method, ApiMetric.created_at >= since)
                .order_by(ApiMetric.duration_ms.desc())
                .limit(1)
                .offset(max(0, int(request_count * 0.05) - 1))
            )
            p95_row = p95_result.scalar()
            summaries.append({
                "endpoint": row.endpoint,
                "method": row.method,
                "avg_duration_ms": round(row.avg_duration_ms, 2),
                "p95_duration_ms": round(p95_row, 2) if p95_row is not None else None,
                "request_count": request_count,
                "error_count": error_count,
                "error_rate": round(error_count / request_count, 4) if request_count > 0 else 0.0,
            })
        return summaries

    async def get_uv_count(self, days: int = 1) -> int:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = (
            await self.db.execute(
                select(func.count(func.distinct(PageView.ip_hash))).where(PageView.created_at >= since)
            )
        ).scalar() or 0
        return result

    async def get_pv_per_minute(self) -> float:
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        result = (
            await self.db.execute(
                select(func.count(PageView.id)).where(PageView.created_at >= since)
            )
        ).scalar() or 0
        return round(result / 60.0, 2)

    async def get_today_comments_count(self) -> int:
        today = datetime.now(timezone.utc).date()
        result = (
            await self.db.execute(
                select(func.count(Comment.id)).where(func.date(Comment.created_at) == today)
            )
        ).scalar() or 0
        return result

    async def get_today_posts_count(self) -> int:
        today = datetime.now(timezone.utc).date()
        result = (
            await self.db.execute(
                select(func.count(Post.id)).where(Post.published == True, func.date(Post.created_at) == today)
            )
        ).scalar() or 0
        return result

    async def get_yesterday_comments_count(self) -> int:
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        result = (
            await self.db.execute(
                select(func.count(Comment.id)).where(func.date(Comment.created_at) == yesterday)
            )
        ).scalar() or 0
        return result

    async def get_yesterday_posts_count(self) -> int:
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        result = (
            await self.db.execute(
                select(func.count(Post.id)).where(Post.published == True, func.date(Post.created_at) == yesterday)
            )
        ).scalar() or 0
        return result

    async def get_trend_daily(self, metric: str, days: int = 7) -> list[dict]:
        today = datetime.now(timezone.utc).date()
        if metric == "comments":
            query = (
                select(
                    func.date(Comment.created_at).label("day"),
                    func.count(Comment.id).label("count"),
                )
                .where(Comment.created_at >= today - timedelta(days=days - 1))
                .group_by(text("day"))
                .order_by(text("day"))
            )
        else:
            query = (
                select(
                    func.date(PageView.created_at).label("day"),
                    func.count(PageView.id).label("count"),
                )
                .where(PageView.created_at >= today - timedelta(days=days - 1))
                .group_by(text("day"))
                .order_by(text("day"))
            )
        result = await self.db.execute(query)
        return [{"date": str(row.day), "count": row.count} for row in result.all()]
