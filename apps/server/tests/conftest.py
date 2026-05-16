import asyncio
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.base import Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true"

SQLITE_COMPATIBLE_TABLES = {
    "posts", "tags", "post_tags", "users", "comments", "media", "page_views", "api_metrics", "post_embeddings", "events",
}


def _patch_models_for_sqlite():
    from app.models.post import PostEmbedding
    from app.models.analytics import Event
    from sqlalchemy import Text
    PostEmbedding.__table__.c.embedding.type = Text()
    Event.__table__.c.event_data.type = Text()


_patch_models_for_sqlite()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        tables_to_create = [
            t for t in Base.metadata.sorted_tables if t.name in SQLITE_COMPATIBLE_TABLES
        ]
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(sync_conn, tables=tables_to_create)
        )
    yield engine
    async with engine.begin() as conn:
        tables_to_drop = [
            t for t in Base.metadata.sorted_tables if t.name in SQLITE_COMPATIBLE_TABLES
        ]
        await conn.run_sync(
            lambda sync_conn: Base.metadata.drop_all(sync_conn, tables=tables_to_drop)
        )
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
        session = TestSession(bind=conn)
        session._test_trans = trans
        session._test_conn = conn
        yield session
        await session.close()
        await trans.rollback()


@pytest_asyncio.fixture
async def redis_mock():
    import fakeredis.aioredis

    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake_redis
    await fake_redis.aclose()


@pytest_asyncio.fixture
async def async_client(db_session, redis_mock):
    from app.core.database import get_db
    from app.core.redis import get_redis
    from app.main import app

    async def override_get_db():
        yield db_session

    async def override_get_redis():
        return redis_mock

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    with patch("app.middleware.rate_limit.redis_client", redis_mock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(redis_mock):
    token_data = {"sub": "test-user-id", "username": "admin"}
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def sample_post(db_session):
    from app.models.post import Post

    post = Post(
        id="test-post-id",
        title="Test Post",
        slug="test-post",
        content="This is test post content that is long enough.",
        excerpt="Test excerpt",
        published=True,
        featured=False,
        view_count=0,
    )
    db_session.add(post)
    await db_session.flush()
    return post


@pytest_asyncio.fixture
async def sample_tag(db_session):
    from app.models.tag import Tag

    tag = Tag(
        id="test-tag-id",
        name="TestTag",
        slug="test-tag",
    )
    db_session.add(tag)
    await db_session.flush()
    return tag


@pytest_asyncio.fixture
async def sample_user(db_session):
    from app.models.user import User

    user = User(
        id="test-user-id",
        username="admin",
        password_hash=hash_password("admin123"),
    )
    db_session.add(user)
    await db_session.flush()
    return user
