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


class AnalyticsOverview(BaseModel):
    total_page_views: int
    today_page_views: int
    total_posts: int
    total_comments: int
    popular_posts: list[dict]
    page_views_daily: list[dict]
    recent_events: list[dict]
