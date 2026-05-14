# ZCW AI Note Blog

<div align="center">

**A full-stack personal blog with AI-powered Q&A — Vue 3 + FastAPI + PostgreSQL + Redis**

**基于 RAG 检索增强生成的 AI 智能问答全栈博客**

[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vuedotjs)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

</div>

---

[English](#english) | [中文](#中文)

---

## English

### Features

**Blog & Content**
- **Markdown Editor** — live preview, syntax highlighting via highlight.js, tag management
- **Tag System** — categorize posts, browse by tag with pagination
- **Full-Text Search** — ILIKE + pg_trgm across title, content, and excerpt
- **Comments** — moderated with rate limiting (3/min per IP)
- **RSS Feed** — auto-generated, Redis-cached with 1-hour TTL

**AI-Powered**
- **RAG Q&A** — chat with your blog via DeepSeek V4 Flash, streaming SSE responses
- **Hybrid Search** — pgvector cosine similarity + pg_trgm keyword match with RRF score fusion
- **AI Summaries** — auto-generated Chinese summaries (50-80 chars) per post
- **Context-Aware** — conversation history in Redis with 1-hour TTL

**Admin Dashboard**
- **Collapsible Sidebar** — icon-only mode, desktop sidebar + mobile drawer
- **Breadcrumbs** — auto-generated from route hierarchy
- **Post Management** — CRUD with unsaved-changes warning and route guards
- **Media Library** — upload with MIME validation, copy URL to clipboard
- **Comment Moderation** — approve/delete with loading states and toast feedback
- **Analytics** — page views, popular posts, daily stats via Redis sorted sets
- **Toast Notifications** — success/error/info with slide-in animation
- **Custom Confirm Dialogs** — styled modal replacing native `confirm()`

**UX & Design**
- **Dark Mode** — system-aware toggle with smooth transitions
- **Responsive** — mobile-first with adaptive sidebar, tables, and grids
- **Glassmorphism** — backdrop-blur AI chat panel
- **Reading Progress** — scroll progress bar on post pages
- **Accessibility** — semantic HTML, `aria-label`, focus-visible rings, sr-only labels

### Architecture

```
┌─────────────────────────────────────────────────┐
│                   Vite Dev Proxy                 │
│         localhost:5173  →  localhost:8000        │
└──────────────┬──────────────────────┬───────────┘
               │                      │
┌──────────────▼──────────┐  ┌───────▼──────────────┐
│       Vue 3 SPA          │  │    FastAPI REST API  │
│                           │  │                      │
│  PublicLayout AdminLayout │  │  /api/v1/posts       │
│  ├─ Header    ├─ Sidebar  │  │  /api/v1/ai/chat     │
│  ├─ Content   ├─ TopBar   │  │  /api/v1/comments    │
│  ├─ Footer    ├─ Content  │  │  /api/v1/rss         │
│  └─ AiChat                │  │  /health             │
│                           │  │                      │
│  Pinia / Vue Router       │  │  SQLAlchemy 2.0 async│
│  Tailwind CSS              │  │  Pydantic v2 / JWT   │
└──────────────┬──────────┘  └───────┬──────────────┘
               │                      │
        ┌──────▼──────────────────────▼──────┐
        │            Docker Compose            │
        │  ┌──────────┐    ┌──────────┐       │
        │  │PostgreSQL│    │  Redis 7 │       │
        │  │16+vector │    │          │       │
        │  └──────────┘    └──────────┘       │
        └──────────────────────────────────────┘
```

**RAG Chat Data Flow:**

```
User Question → /api/v1/ai/chat/stream
  → pgvector cosine distance search (top-K chunks)
  → pg_trgm keyword search (supplementary)
  → RRF reciprocal rank fusion
  → Build context from matched chunks
  → DeepSeek V4 Flash (SSE streaming)
  → Token-by-token response to browser
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Vue 3 + TypeScript | Composition API, `<script setup>`, type safety |
| | Tailwind CSS 3 | Utility-first styling, dark mode |
| | Pinia | Auth & theme state management |
| | Vue Router 4 | Nested routes, auth guards, scroll behavior |
| | marked + highlight.js | Markdown rendering with code highlighting |
| **Backend** | FastAPI | Async REST API, auto OpenAPI docs |
| | SQLAlchemy 2.0 | Async ORM with `selectinload` eager loading |
| | Pydantic v2 | Request/response validation |
| | python-jose | JWT generation & verification |
| | passlib + bcrypt | Password hashing |
| **Database** | PostgreSQL 16 | Primary data store |
| | pgvector | Vector embeddings for semantic search |
| | pg_trgm | Trigram fuzzy matching for text search |
| **Cache** | Redis 7 | API caching, rate limiting, sorted sets, sessions |
| **AI** | DeepSeek V4 Flash | LLM for RAG chat & summarization |
| | OpenAI Embeddings | Text → 1536-dimension vector |
| **Infra** | Docker Compose | PostgreSQL + Redis containers |
| | Vite | Dev server with HMR & API proxy |
| | Uvicorn | ASGI server |

### Design Decisions

**Why Vue 3 + FastAPI instead of Next.js or Nuxt?**

This is a personal blog, not an SSR-dependent content site. A pure SPA + REST API split gives cleaner boundaries, easier debugging, and more transferable skills — the same patterns apply to any frontend/backend separation in production.

**Why DeepSeek V4 Flash for chat but OpenAI for embeddings?**

DeepSeek does not provide an embeddings API. Both are OpenAI-compatible, so swapping providers only requires changing environment variables — no code changes needed. See `config.py` for the clean separation between chat and embedding configuration.

**Why PostgreSQL + pgvector instead of a dedicated vector DB?**

For a personal blog with hundreds (not millions) of documents, pgvector is more than sufficient. One database for both structured data and vectors — no extra infrastructure. The hybrid search (vector + trigram) outperforms pure vector search at this scale.

**Why Redis sorted sets for analytics?**

Redis `ZINCRBY` is O(log N) and atomic — no race conditions. The `increment_view_count` function updates the ORM object, and Redis independently tracks popularity rankings without blocking the main write path.

**Why two layout components instead of a single app shell?**

`PublicLayout.vue` (Header + Footer + AiChat) and `AdminLayout.vue` (Sidebar + TopBar + Breadcrumbs) are fully independent. Admin pages never load the public Header or AI chat widget — clean separation without router meta hacks.

**Why CSS-animated Toasts & ConfirmDialogs instead of a UI library?**

Zero runtime dependencies beyond Vue itself. The dialogs, toasts, transitions, and layout components total under 400 lines of code, all fully typed. No lock-in to a third-party design system.

### Project Structure

```
zcw-ai-note-blog/
├── docker-compose.yml              # PostgreSQL 16 (pgvector) + Redis 7
├── .env.example                    # Environment template
├── .env                            # Local secrets (git-ignored)
│
├── apps/
│   ├── web/                        # Vue 3 Frontend
│   │   ├── src/
│   │   │   ├── api/                # Axios instance + per-resource modules
│   │   │   ├── components/
│   │   │   │   ├── ai/             # AiChat (floating widget, SSE streaming)
│   │   │   │   ├── blog/           # PostCard, CommentSection, PostNavigation
│   │   │   │   ├── layout/        # Header, Footer
│   │   │   │   └── ui/            # BaseSkeleton, BaseEmptyState, Toast, ConfirmDialog
│   │   │   ├── composables/        # usePostData, useMarkdown, useToast, useConfirm
│   │   │   ├── layouts/            # PublicLayout, AdminLayout
│   │   │   ├── pages/
│   │   │   │   ├── public/         # Home, Post, Tags, Search, About, NotFound
│   │   │   │   └── admin/          # Dashboard, PostList, PostEditor, CommentList, Media
│   │   │   ├── router/             # Route definitions + guards + 404
│   │   │   ├── services/           # SEO meta + JSON-LD
│   │   │   ├── stores/             # auth (Pinia), theme (Pinia)
│   │   │   ├── tracking/           # Client-side analytics with sendBeacon
│   │   │   ├── types/              # TypeScript interfaces
│   │   │   └── utils/              # constants.ts
│   │   ├── index.html
│   │   ├── vite.config.ts          # Proxy /api → :8000, chunk splitting
│   │   └── tailwind.config.js
│   │
│   └── server/                     # FastAPI Backend
│       ├── app/
│       │   ├── api/v1/             # Route modules (posts, comments, auth, ai, rss, analytics)
│       │   ├── core/               # config, database, redis, security
│       │   ├── middleware/         # Telemetry middleware
│       │   ├── models/             # ORM: Post, Tag, Comment, User, Media, Analytics
│       │   ├── schemas/            # Pydantic request/response models
│       │   ├── services/           # post, comment, ai, rag, cache, analytics
│       │   └── utils/              # Exceptions, pagination helpers
│       ├── alembic/                # Database migrations
│       └── requirements.txt
```

### Quick Start

**Prerequisites:** Python 3.11+ / Node.js 20+ / Docker Desktop

```bash
# 1. Start databases
docker compose up -d

# 2. Configure environment
cp .env.example .env
# Edit .env with your DeepSeek and OpenAI API keys

# 3. Install & run backend
cd apps/server
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Install & run frontend
cd apps/web
npm install
npm run dev

# 5. Initialize database & create admin
cd apps/server
python -c "
import asyncio
from app.models.base import Base
from app.models import *
from app.core.database import engine
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
"

# 6. Open
# Blog:    http://localhost:5173
# Admin:   http://localhost:5173/admin
# API Docs: http://localhost:8000/docs
# Login:   admin / admin123
```

| Env Variable | Description | Default |
|-------------|-------------|---------|
| `OPENAI_API_KEY` | DeepSeek API key | *required* |
| `OPENAI_BASE_URL` | LLM endpoint | `https://api.deepseek.com` |
| `OPENAI_MODEL` | LLM model | `deepseek-v4-flash` |
| `EMBEDDING_API_KEY` | OpenAI API key for embeddings | *required* |
| `EMBEDDING_BASE_URL` | Embedding endpoint | `https://api.openai.com/v1` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `SITE_URL` | Public site URL | `http://localhost:5173` |
| `SITE_NAME` | Blog name | `My Blog` |
| `JWT_SECRET_KEY` | JWT signing key | *change me* |

### API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v1/posts` | — | Paginated list |
| `GET` | `/api/v1/posts/search?q=` | — | Full-text search |
| `GET` | `/api/v1/posts/{slug}` | — | Detail with tags + nav |
| `GET` | `/api/v1/posts/{slug}/summary` | — | AI summary (7d cache) |
| `GET` | `/api/v1/tags` | — | All tags with counts |
| `POST` | `/api/v1/comments` | — | Submit (3/min/IP) |
| `POST` | `/api/v1/ai/chat` | — | RAG chat |
| `POST` | `/api/v1/ai/chat/stream` | — | RAG chat SSE |
| `GET` | `/api/v1/rss` | — | RSS 2.0 feed |
| `POST` | `/api/v1/auth/login` | — | Login (5/min/IP) |
| `GET/POST/PUT/DELETE` | `/api/v1/admin/*` | Bearer | Admin CRUD |
| `GET` | `/health` | — | Redis + DB ping |

### Security

- **JWT authentication** with configurable expiration
- **bcrypt** password hashing via passlib
- **Rate limiting** — login 5/min, comments 3/min per IP
- **File upload** — extension + MIME double validation
- **IP hashing** — SHA-256 for rate limit keys, raw IPs never stored
- **CORS whitelist** — configured origins only
- **401 interceptor** — auto-redirect to login, clear token
- **`.env` git-ignored** — no secrets in version control

### Roadmap

- [ ] GitHub Actions CI — lint + type-check + build
- [ ] pytest — API integration tests
- [ ] vitest — component tests
- [ ] Docker production image
- [ ] ESLint + Prettier
- [ ] Draft auto-save in PostEditor
- [ ] Image paste/drag-drop in editor
- [ ] i18n English/Chinese

### License

MIT

---

## 中文

### 功能

**博客与内容**
- **Markdown 编辑器** — 实时预览、highlight.js 代码高亮、标签管理
- **标签系统** — 文章分类、按标签浏览、分页
- **全文搜索** — ILIKE + pg_trgm 模糊搜索标题、正文和摘要
- **评论系统** — 审核机制 + IP 限流（3次/分钟）
- **RSS 订阅** — 自动生成，Redis 缓存 1 小时

**AI 功能**
- **RAG 智能问答** — 基于博客内容的检索增强生成问答，SSE 流式响应
- **混合检索** — pgvector 余弦相似度 + pg_trgm 关键词匹配，RRF 融合排序
- **AI 摘要** — 自动生成每篇文章的中文摘要（50-80字）
- **上下文记忆** — 对话历史存储在 Redis，1 小时有效

**管理后台**
- **可折叠侧边栏** — 图标模式/完整模式切换，桌面侧边栏 + 移动端抽屉
- **面包屑导航** — 根据路由层级自动生成
- **文章管理** — 增删改查、未保存提醒、路由离开守卫
- **媒体库** — 图片上传（MIME 校验）、一键复制 URL
- **评论审核** — 通过/删除带 loading 状态和 Toast 反馈
- **数据统计** — 页面访问、热门文章、日活统计（Redis 有序集合）
- **Toast 通知** — 成功/错误/提示消息，滑入动画自动消失
- **自定义确认框** — 替代浏览器原生 confirm()

**体验与设计**
- **暗色模式** — 跟随系统主题切换，平滑过渡
- **响应式** — 移动端优先，自适应侧边栏、表格、网格
- **玻璃拟态** — AI 对话面板毛玻璃效果
- **阅读进度条** — 文章页滚动进度指示
- **无障碍** — 语义化 HTML、aria-label、focus-visible 焦点环、sr-only 标签

### 架构

```
┌─────────────────────────────────────────────────┐
│                  Vite 开发代理                     │
│         localhost:5173  →  localhost:8000        │
└──────────────┬──────────────────────┬───────────┘
               │                      │
┌──────────────▼──────────┐  ┌───────▼──────────────┐
│       Vue 3 单页应用      │  │    FastAPI REST API  │
│                           │  │                      │
│  PublicLayout AdminLayout │  │  /api/v1/posts       │
│  ├─ Header    ├─ 侧边栏   │  │  /api/v1/ai/chat     │
│  ├─ 内容区    ├─ 顶栏     │  │  /api/v1/comments    │
│  ├─ Footer    ├─ 内容区   │  │  /api/v1/rss         │
│  └─ AiChat                │  │  /health             │
│                           │  │                      │
│  Pinia / Vue Router       │  │  SQLAlchemy 2.0 异步  │
│  Tailwind CSS              │  │  Pydantic v2 / JWT   │
└──────────────┬──────────┘  └───────┬──────────────┘
               │                      │
        ┌──────▼──────────────────────▼──────┐
        │            Docker Compose            │
        │  ┌──────────┐    ┌──────────┐       │
        │  │PostgreSQL│    │  Redis 7 │       │
        │  │16+向量   │    │          │       │
        │  └──────────┘    └──────────┘       │
        └──────────────────────────────────────┘
```

**RAG 对话数据流：**

```
用户提问 → /api/v1/ai/chat/stream
  → pgvector 余弦相似度检索（Top-K 文本块）
  → pg_trgm 关键词检索（补充召回）
  → RRF 倒数排名融合
  → 拼接检索到的上下文
  → DeepSeek V4 Flash（SSE 流式生成）
  → 逐 token 返回浏览器
```

### 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **前端** | Vue 3 + TypeScript | Composition API、`<script setup>`、类型安全 |
| | Tailwind CSS 3 | 原子化样式、暗色模式 |
| | Pinia | 认证与主题状态管理 |
| | Vue Router 4 | 嵌套路由、权限守卫、滚动行为 |
| | marked + highlight.js | Markdown 渲染与代码高亮 |
| **后端** | FastAPI | 异步 REST API，自动生成 OpenAPI 文档 |
| | SQLAlchemy 2.0 | 异步 ORM，`selectinload` 预加载 |
| | Pydantic v2 | 请求/响应数据校验 |
| | python-jose | JWT 令牌生成与验证 |
| | passlib + bcrypt | 密码哈希 |
| **数据库** | PostgreSQL 16 | 主数据存储 |
| | pgvector | 向量嵌入语义搜索 |
| | pg_trgm | 三元组模糊匹配 |
| **缓存** | Redis 7 | API 缓存、限流、有序集合、会话管理 |
| **AI** | DeepSeek V4 Flash | RAG 对话与文章摘要 |
| | OpenAI Embeddings | 文本 → 1536 维向量 |
| **基础设施** | Docker Compose | PostgreSQL + Redis 容器 |
| | Vite | 开发服务器 HMR + API 代理 |
| | Uvicorn | ASGI 服务器 |

### 设计决策

**为什么用 Vue 3 + FastAPI 而不是 Next.js 或 Nuxt？**

个人博客不需要 SSR。纯 SPA + REST API 的分离架构边界清晰、调试方便，且前后端模式可迁移到任何项目。

**为什么对话用 DeepSeek V4 Flash，嵌入向量用 OpenAI？**

DeepSeek 没有提供嵌入 API。两者都是 OpenAI 兼容格式，切换供应商只需修改环境变量，无需改代码。`config.py` 中已将聊天和嵌入配置分离。

**为什么用 PostgreSQL + pgvector 而不是独立的向量数据库？**

个人博客文档量级为数百篇，pgvector 完全够用。一套数据库同时处理结构化数据和向量检索，无需额外基础设施。混合检索（向量 + trigram）在此规模下效果优于纯向量检索。

**为什么用 Redis 有序集合做统计？**

`ZINCRBY` 操作 O(log N) 且原子性——无竞态条件。`increment_view_count` 直接操作 ORM 对象，Redis 独立跟踪热度排名，不阻塞主写入路径。

**为什么用两个布局组件而不是单 App Shell？**

`PublicLayout.vue`（Header + Footer + AiChat）和 `AdminLayout.vue`（侧边栏 + 顶栏 + 面包屑）完全独立。后台页面不会加载前台导航或 AI 对话组件，干净利落。

**为什么 CSS 动画 Toast/ConfirmDialog 而不是引入 UI 库？**

零运行时依赖，仅 Vue 本身。对话框、Toast、过渡动画、布局组件总共不到 400 行代码，全部类型安全。不绑定任何第三方设计系统。

### 项目结构

```
zcw-ai-note-blog/
├── docker-compose.yml              # PostgreSQL 16 (pgvector) + Redis 7
├── .env.example                    # 环境变量模板
├── .env                            # 本地密钥（git 忽略）
│
├── apps/
│   ├── web/                        # Vue 3 前端
│   │   ├── src/
│   │   │   ├── api/                # Axios 实例 + 各模块请求
│   │   │   ├── components/
│   │   │   │   ├── ai/             # AiChat 浮动对话组件
│   │   │   │   ├── blog/           # PostCard、CommentSection、PostNavigation
│   │   │   │   ├── layout/        # Header、Footer
│   │   │   │   └── ui/            # BaseSkeleton、Toast、ConfirmDialog
│   │   │   ├── composables/        # usePostData、useMarkdown、useToast、useConfirm
│   │   │   ├── layouts/            # PublicLayout、AdminLayout
│   │   │   ├── pages/
│   │   │   │   ├── public/         # 首页、文章、标签、搜索、关于、404
│   │   │   │   └── admin/          # 仪表板、文章管理、编辑器、评论、媒体
│   │   │   ├── router/             # 路由定义 + 守卫 + 404
│   │   │   ├── services/           # SEO 元标签 + JSON-LD
│   │   │   ├── stores/             # auth、theme (Pinia)
│   │   │   ├── tracking/           # 客户端埋点（sendBeacon）
│   │   │   ├── types/              # TypeScript 类型定义
│   │   │   └── utils/              # constants.ts
│   │   └── vite.config.ts          # 代理 /api → :8000，代码分包
│   │
│   └── server/                     # FastAPI 后端
│       ├── app/
│       │   ├── api/v1/             # 路由模块
│       │   ├── core/               # 配置、数据库、Redis、安全
│       │   ├── middleware/         # 遥测中间件
│       │   ├── models/             # ORM 模型
│       │   ├── schemas/            # Pydantic 校验
│       │   ├── services/           # 业务逻辑
│       │   └── utils/              # 异常、分页工具
│       └── requirements.txt
```

### 快速开始

**前置要求：** Python 3.11+ / Node.js 20+ / Docker Desktop

```bash
# 1. 启动数据库
docker compose up -d

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DeepSeek 和 OpenAI API Key

# 3. 安装并启动后端
cd apps/server
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 安装并启动前端
cd apps/web
npm install
npm run dev

# 5. 初始化数据库并创建管理员
cd apps/server
python -c "
import asyncio
from app.models.base import Base
from app.models import *
from app.core.database import engine
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
"

# 6. 访问
# 博客首页：  http://localhost:5173
# 管理后台：  http://localhost:5173/admin
# API 文档：  http://localhost:8000/docs
# 默认账号：  admin / admin123
```

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `OPENAI_API_KEY` | DeepSeek API 密钥 | *必填* |
| `OPENAI_BASE_URL` | LLM 接口地址 | `https://api.deepseek.com` |
| `OPENAI_MODEL` | LLM 模型 | `deepseek-v4-flash` |
| `EMBEDDING_API_KEY` | OpenAI API 密钥（嵌入） | *必填* |
| `EMBEDDING_BASE_URL` | 嵌入接口地址 | `https://api.openai.com/v1` |
| `EMBEDDING_MODEL` | 嵌入模型 | `text-embedding-3-small` |
| `SITE_URL` | 站点 URL（RSS 用） | `http://localhost:5173` |
| `SITE_NAME` | 博客名称 | `My Blog` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | *务必修改* |

### API 概览

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| `GET` | `/api/v1/posts` | — | 分页列表 |
| `GET` | `/api/v1/posts/search?q=` | — | 全文搜索 |
| `GET` | `/api/v1/posts/{slug}` | — | 文章详情 |
| `GET` | `/api/v1/posts/{slug}/summary` | — | AI 摘要（缓存 7 天） |
| `GET` | `/api/v1/tags` | — | 标签列表 |
| `POST` | `/api/v1/comments` | — | 提交评论（限流 3次/分钟） |
| `POST` | `/api/v1/ai/chat` | — | RAG 对话（非流式） |
| `POST` | `/api/v1/ai/chat/stream` | — | RAG 流式对话（SSE） |
| `GET` | `/api/v1/rss` | — | RSS 2.0 订阅 |
| `POST` | `/api/v1/auth/login` | — | 管理员登录（限流 5次/分钟） |
| `GET/POST/PUT/DELETE` | `/api/v1/admin/*` | Bearer | 后台管理 |
| `GET` | `/health` | — | 健康检查 |

### 安全措施

- **JWT 认证** — 可配置过期时间
- **bcrypt 密码哈希** — 通过 passlib 实现
- **接口限流** — 登录 5次/分钟，评论 3次/分钟
- **文件上传校验** — 扩展名 + MIME 类型双重验证
- **IP 哈希** — SHA-256 哈希用于限流键，不存储原始 IP
- **CORS 白名单** — 仅允许配置的来源
- **401 拦截** — 自动跳转登录页，清除令牌
- **`.env` git 忽略** — 密钥不入版本控制

### 路线图

- [ ] GitHub Actions CI — lint + 类型检查 + 构建
- [ ] pytest — API 集成测试
- [ ] vitest — 组件测试
- [ ] Docker 生产镜像
- [ ] ESLint + Prettier
- [ ] 编辑器草稿自动保存
- [ ] 编辑器图片粘贴/拖拽上传
- [ ] 中英文国际化

### 开源协议

MIT
