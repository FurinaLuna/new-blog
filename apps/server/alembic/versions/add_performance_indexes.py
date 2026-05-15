add_performance_indexes

Revision ID: add_perf_idx
Revises:
Create Date: 2026-05-15

"""
Add performance indexes for posts, comments, page_views, events, api_metrics.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


def upgrade() -> None:
    op.create_index("idx_posts_published_featured", "posts", ["published", "featured"])
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_posts_content_tsvector "
        "ON posts USING GIN (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,'')))"
    ))
    op.create_index("idx_comments_created_at", "comments", ["created_at"])
    op.create_index("idx_page_views_session", "page_views", ["session_id"])
    op.create_index("idx_events_session", "events", ["session_id"])
    op.create_index("idx_api_metrics_status", "api_metrics", ["status_code", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_api_metrics_status", table_name="api_metrics")
    op.drop_index("idx_events_session", table_name="events")
    op.drop_index("idx_page_views_session", table_name="page_views")
    op.drop_index("idx_comments_created_at", table_name="comments")
    op.execute(text("DROP INDEX IF EXISTS idx_posts_content_tsvector"))
    op.drop_index("idx_posts_published_featured", table_name="posts")
