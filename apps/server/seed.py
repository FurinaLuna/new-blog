"""Seed script: create admin user and sample posts."""
import asyncio
from sqlalchemy import select, text
from app.models.base import Base
from app.core.database import async_session, engine
from app.core.security import hash_password
from app.models.user import User
from app.models.post import Post
from app.models.tag import Tag
from app.models.post import PostTag


SAMPLE_POSTS = [
    {
        "title": "Hello World — 我的第一篇博客",
        "slug": "hello-world",
        "content": """欢迎来到我的个人博客！这是第一篇博文。

## 关于这个博客

这个博客由 Vue 3 + FastAPI + PostgreSQL 构建，支持 Markdown 写作、标签分类、评论、RSS、AI 问答等功能。

## 为什么写博客

写博客的目的是记录学习和思考的过程。通过文字整理知识，既是对自己的梳理，也希望能帮助到他人。

> "写作是对思维最严格的训练。" —— Walter Kaufmann

## 技术栈

- **前端**: Vue 3 + TypeScript + Tailwind CSS
- **后端**: FastAPI + SQLAlchemy
- **数据库**: PostgreSQL + pgvector
- **缓存**: Redis

希望这个博客能持续更新！""",
        "excerpt": "欢迎来到我的个人博客！这是第一篇博文，介绍博客的构建目的和技术栈。",
        "published": True,
        "featured": True,
    },
    {
        "title": "FastAPI 异步数据库操作最佳实践",
        "slug": "fastapi-async-db-best-practices",
        "content": """FastAPI 作为 Python 生态中最受欢迎的异步 Web 框架，与异步数据库的配合至关重要。

## 为什么选择异步？

传统的同步 WSGI 框架使用线程池处理并发，而 FastAPI 基于 ASGI，使用事件循环。

### 优势
- **更高吞吐**: 单个进程处理更多请求
- **更少资源**: 不需要大量线程
- **更简洁代码**: async/await 语法

### 劣势
- 需要注意阻塞操作
- 调试相对复杂

## SQLAlchemy 异步配置

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=False,
    pool_size=10,
    max_overflow=20,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)
```

## 连接池管理

重要参数：
- `pool_size`: 连接池大小，建议 CPU 核心数 * 2
- `max_overflow`: 超出 pool_size 后的最大额外连接
- `pool_recycle`: 连接回收时间（秒），防止 PG 断开空闲连接

## 常见陷阱

1. **不要在 async 函数中使用同步查询**
2. **记得 flush 获取自增 ID**
3. **注意 lazy loading 触发额外查询**

希望这篇文章对你有所帮助！""",
        "excerpt": "深入探讨 FastAPI 中异步数据库操作的最佳实践，包括连接池配置、常见陷阱和性能优化技巧。",
        "published": True,
        "featured": True,
    },
    {
        "title": "Docker Compose 多服务编排实战",
        "slug": "docker-compose-multi-service",
        "content": """Docker Compose 是本地开发和测试环境的神器。

## 基本概念

Docker Compose 使用 YAML 文件定义多个服务，一键启动整个应用栈。

```yaml
version: "3.9"
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: blog
      POSTGRES_PASSWORD: blog_secret
      POSTGRES_DB: blog
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## 健康检查

为每个服务配置 healthcheck，确保服务就绪后才启动依赖方：

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U blog"]
  interval: 5s
  timeout: 5s
  retries: 5
```

## 数据持久化

使用 named volumes 持久化数据，避免容器删除后数据丢失。""",
        "excerpt": "学习如何使用 Docker Compose 编排多服务应用，包括 PostgreSQL、Redis 的配置和健康检查。",
        "published": True,
        "featured": False,
    },
    {
        "title": "Vue 3 Composition API 与 TypeScript 实战",
        "slug": "vue3-composition-api-typescript",
        "content": """Vue 3 的 Composition API 是组织组件逻辑的现代方式。

## setup 语法糖

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Post {
  id: string
  title: string
  slug: string
}

const posts = ref<Post[]>([])
const loading = ref(false)

const featuredPosts = computed(() =>
  posts.value.filter(p => p.featured)
)

onMounted(async () => {
  loading.value = true
  const res = await fetch('/api/v1/posts')
  posts.value = await res.json()
  loading.value = false
})
</script>
```

## 组合函数

```typescript
// composables/usePosts.ts
export function usePosts() {
  const posts = ref<Post[]>([])
  const loading = ref(false)

  async function fetchPosts() {
    loading.value = true
    // fetch logic
    loading.value = false
  }

  return { posts, loading, fetchPosts }
}
```

Composition API 让逻辑复用变得异常简单。""",
        "excerpt": "结合 TypeScript 使用 Vue 3 Composition API 的最佳实践，包括 setup 语法糖和组合函数。",
        "published": True,
        "featured": False,
    },
    {
        "title": "搭建 RAG 问答系统的完整指南",
        "slug": "rag-system-guide",
        "content": """RAG（Retrieval-Augmented Generation）是目前最流行的 AI 应用模式。

## RAG 工作流程

1. **文档切分**: 将长文档切分为 chunks
2. **向量化**: 调用 Embedding API 将 chunks 转为向量
3. **存储**: 将向量存入向量数据库（如 pgvector）
4. **检索**: 用户提问时，将问题向量化，搜索最相似的 chunks
5. **生成**: 将检索到的内容作为上下文，调用 LLM 生成回答

## 分块策略

```python
def split_text(text: str, chunk_size: int = 500) -> list[str]:
    paragraphs = text.split("\\n\\n")
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) <= chunk_size:
            current += p + "\\n\\n"
        else:
            chunks.append(current.strip())
            current = p + "\\n\\n"
    if current:
        chunks.append(current.strip())
    return chunks
```

## pgvector 向量搜索

```sql
SELECT content, 1 - (embedding <=> :query_vector) AS similarity
FROM post_embeddings
ORDER BY embedding <=> :query_vector
LIMIT 5;
```

## 优化技巧

- 召回率优先于精确率
- 使用重排序（re-ranking）提升精确度
- 缓存常见问题的 embedding""",
        "excerpt": "从零搭建 RAG 问答系统，涵盖文档切分、向量化、pgvector 搜索和 LLM 生成的全流程。",
        "published": True,
        "featured": False,
    },
]

TAGS = [
    {"name": "技术", "slug": "tech"},
    {"name": "前端", "slug": "frontend"},
    {"name": "后端", "slug": "backend"},
    {"name": "AI", "slug": "ai"},
    {"name": "DevOps", "slug": "devops"},
]

# Map posts to tags: post slug -> tag slugs
POST_TAG_MAP = {
    "hello-world": ["tech"],
    "fastapi-async-db-best-practices": ["backend", "tech"],
    "docker-compose-multi-service": ["devops", "tech"],
    "vue3-composition-api-typescript": ["frontend", "tech"],
    "rag-system-guide": ["ai", "tech", "backend"],
}


async def seed():
    # Create tables first
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

    async with async_session() as db:
        # Create admin user
        existing = (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
        if not existing:
            db.add(User(username="admin", password_hash=hash_password("admin123")))
            print("Admin user created (admin / admin123)")

        # Create tags
        tag_objects = {}
        for tag_data in TAGS:
            existing_tag = (await db.execute(select(Tag).where(Tag.slug == tag_data["slug"]))).scalar_one_or_none()
            if existing_tag:
                tag_objects[existing_tag.slug] = existing_tag
            else:
                tag = Tag(**tag_data)
                db.add(tag)
                tag_objects[tag_data["slug"]] = tag

        await db.flush()

        # Create posts
        for post_data in SAMPLE_POSTS:
            existing_post = (await db.execute(select(Post).where(Post.slug == post_data["slug"]))).scalar_one_or_none()
            if not existing_post:
                tag_slugs = POST_TAG_MAP.get(post_data["slug"], [])
                post_tags = [PostTag(tag_id=tag_objects[s].id) for s in tag_slugs]

                post = Post(
                    title=post_data["title"],
                    slug=post_data["slug"],
                    content=post_data["content"],
                    excerpt=post_data.get("excerpt"),
                    published=post_data.get("published", False),
                    featured=post_data.get("featured", False),
                    tags=post_tags,
                )
                db.add(post)
                print(f"Sample post created: {post.title}")

        await db.commit()
        print("Seed completed!")


if __name__ == "__main__":
    asyncio.run(seed())
