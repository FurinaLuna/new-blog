# zcw-ai-note-blog

个人技术博客全栈项目，Vue 3 + FastAPI + PostgreSQL + Redis 技术栈，支持文章管理、AI 智能问答、RAG 检索增强生成。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3, TypeScript, Tailwind CSS, Pinia, Vue Router |
| 后端 | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| 数据库 | PostgreSQL 16 + pgvector (向量检索) |
| 缓存 | Redis 7 |
| AI | DeepSeek V4 Flash (对话), OpenAI (嵌入向量) |
| 部署 | Docker Compose, Vite, Uvicorn |

## 功能

- Markdown 文章编辑与发布
- 标签分类、全文搜索
- 评论审核
- AI 智能问答（RAG 检索增强生成）
- AI 文章摘要
- RSS 订阅
- 暗色模式
- 访问统计与分析
- 响应式设计

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 20+
- Docker Desktop（数据库和缓存）

### 1. 启动基础设施

```bash
docker compose up -d
```

启动 PostgreSQL (5432) 和 Redis (6379)。

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入 API Key：

```env
# DeepSeek AI 对话
OPENAI_API_KEY=sk-<your-deepseek-api-key>
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash

# OpenAI 嵌入向量（DeepSeek 不支持）
EMBEDDING_API_KEY=sk-<your-openai-api-key>
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

# 站点信息
SITE_URL=http://localhost:5173
SITE_NAME=My Blog
```

### 3. 启动后端

```bash
cd apps/server
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端运行在 http://localhost:8000，API 文档在 http://localhost:8000/docs。

### 4. 启动前端

```bash
cd apps/web
npm install
npm run dev
```

前端运行在 http://localhost:5173。

### 5. 初始化数据库

首次运行需要创建数据库表：

```bash
cd apps/server
python -c "
import asyncio
from app.models.base import Base
from app.models import *
from app.core.database import engine

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Done')

asyncio.run(init())
"
```

同时需要创建管理员账户：

```bash
python -c "
import asyncio
from app.models.user import User
from app.core.security import hash_password
from app.core.database import async_session

async def seed():
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == 'admin'))
        if not result.scalar_one_or_none():
            session.add(User(username='admin', password_hash=hash_password('admin123'), display_name='Admin'))
            await session.commit()

asyncio.run(seed())
"
```

### 6. 访问

- 前台：http://localhost:5173
- 后台：http://localhost:5173/admin
- 默认账号：`admin` / `admin123`

## 项目结构

```
├── docker-compose.yml          # PostgreSQL + Redis
├── .env / .env.example         # 环境变量
│
├── apps/web/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # Axios 请求封装
│   │   ├── components/
│   │   │   ├── ai/             # AI 对话组件
│   │   │   ├── blog/           # 文章/评论组件
│   │   │   ├── layout/         # 布局（Header/Footer/Sidebar）
│   │   │   └── ui/             # 通用 UI（Skeleton/EmptyState）
│   │   ├── composables/        # Vue Composables
│   │   ├── pages/
│   │   │   ├── public/         # 前台页面
│   │   │   └── admin/          # 后台页面
│   │   ├── router/             # Vue Router
│   │   ├── services/           # SEO 服务
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── tracking/           # 埋点分析
│   │   ├── types/              # TypeScript 类型
│   │   └── utils/              # 常量/工具
│   └── vite.config.ts
│
├── apps/server/                # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/             # REST API 路由
│   │   ├── core/               # 配置/数据库/安全/Redis
│   │   ├── middleware/         # 中间件
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic 校验
│   │   ├── services/           # 业务逻辑
│   │   └── utils/              # 工具函数
│   └── requirements.txt
```

## API 概览

| 端点 | 说明 |
|------|------|
| `GET /api/v1/posts` | 文章列表（分页、标签过滤、搜索） |
| `GET /api/v1/posts/:slug` | 文章详情 |
| `GET /api/v1/posts/:slug/summary` | AI 摘要 |
| `GET /api/v1/tags` | 标签列表 |
| `POST /api/v1/comments` | 提交评论 |
| `POST /api/v1/ai/chat` | AI 对话 |
| `POST /api/v1/ai/chat/stream` | AI 流式对话（SSE） |
| `GET /api/v1/rss` | RSS Feed |
| `POST /api/v1/auth/login` | 管理员登录 |
| `GET /health` | 健康检查 |
