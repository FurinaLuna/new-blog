from datetime import datetime, date
from pydantic import BaseModel


class AnalyticsEventIn(BaseModel):
    event_type: str
    event_data: dict | None = {}
    source_page: str
    session_id: str


class PageViewOut(BaseModel):
    id: str
    path: str
    referrer: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EventOut(BaseModel):
    id: str
    event_type: str
    event_data: dict
    source_page: str
    session_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiMetricOut(BaseModel):
    id: str
    endpoint: str
    method: str
    status_code: int
    duration_ms: float
    created_at: datetime

    model_config = {"from_attributes": True}


class DailyStat(BaseModel):
    date: str
    count: int


class PopularPost(BaseModel):
    slug: str
    title: str
    views: int


class GrowthRate(BaseModel):
    pv: float
    comments: float
    posts: float


class TopTag(BaseModel):
    name: str
    slug: str
    post_count: int


class ApiPerformanceSummary(BaseModel):
    endpoint: str
    method: str
    avg_duration_ms: float
    p95_duration_ms: float | None
    request_count: int
    error_count: int
    error_rate: float


class RealtimeStats(BaseModel):
    online_users: int
    today_pv: int
    today_uv: int
    pv_per_minute: float


class AnalyticsOverview(BaseModel):
    total_page_views: int
    today_page_views: int
    yesterday_page_views: int = 0
    total_posts: int
    total_comments: int
    total_drafts: int = 0
    pending_comments: int = 0
    growth_rate: GrowthRate | None = None
    popular_posts: list[PopularPost] = []
    page_views_daily: list[DailyStat] = []
    comments_daily: list[DailyStat] = []
    top_tags: list[TopTag] = []
    recent_events: list[dict]
