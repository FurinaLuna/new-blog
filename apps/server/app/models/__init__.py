from app.models.base import Base

# Import all models so alembic can discover them
from app.models.post import Post
from app.models.tag import Tag
from app.models.user import User
from app.models.comment import Comment
from app.models.media import Media
from app.models.analytics import PageView, Event, ApiMetric
