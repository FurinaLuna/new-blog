# ZCW AI Note Blog

<div align="center">

**A full-stack personal blog with AI-powered Q&A — built with Vue 3, FastAPI, PostgreSQL & Redis.**

[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vuedotjs)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

</div>

---

## Features

### Blog & Content
- **Markdown Editor** — write with live preview, syntax highlighting (highlight.js), tag management
- **Tag System** — categorize posts with tags, browse by tag with pagination
- **Full-Text Search** — search across title, content, and excerpt with ILIKE + pg_trgm
- **Comments** — moderated comments with rate limiting (3/min per IP)
- **RSS Feed** — auto-generated feed with Redis caching (1-hour TTL)

### AI-Powered
- **RAG Q&A** — chat with your blog content via DeepSeek V4 Flash, with streaming SSE responses
- **Hybrid Search** — pgvector cosine similarity + pg_trgm keyword matching with RRF score fusion
- **AI Summaries** — auto-generated Chinese summaries (50-80 chars) for each post
- **Context-Aware** — conversation history stored in Redis (1-hour TTL)

### Admin Dashboard
- **Collapsible Sidebar** — icon-only mode for focused editing, desktop + mobile drawer
- **Breadcrumbs** — auto-generated from route hierarchy
- **Post Management** — create, edit, delete with unsaved-changes warnings and route guards
- **Media Library** — image upload with MIME validation, copy-to-clipboard URL
- **Comment Moderation** — approve/delete with loading states and toast feedback
- **Analytics** — page views, popular posts, daily stats with Redis sorted sets
- **Toast Notifications** — success/error/info feedback with auto-dismiss and slide-in animation
- **Custom Confirm Dialogs** — styled modal replacement for native `confirm()`

### UX & Design
- **Dark Mode** — system-aware theme toggle with smooth transitions
- **Responsive** — mobile-first with adaptive sidebar, tables, and grids
- **Glassmorphism** — backdrop-blur panels for the AI chat widget
- **Progress Bar** — reading progress indicator on post pages
- **Accessibility** — semantic HTML, `aria-label`, focus-visible rings, sr-only labels

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Vite Dev Proxy                  │
│         localhost:5173  →  localhost:8000         │
└──────────────┬──────────────────────┬────────────┘
               │                      │
┌──────────────▼──────────┐  ┌───────▼──────────────┐
│       Vue 3 SPA          │  │    FastAPI REST API   │
│                           │  │                       │
│  PublicLayout  AdminLayout│  │  /api/v1/posts        │
│  ├─ Header     ├─ Sidebar │  │  /api/v1/ai/chat      │
│  ├─ router-view├─ TopBar  │  │  /api/v1/comments     │
│  ├─ Footer     ├─ Content │  │  /api/v1/rss          │
│  └─ AiChat                │  │  /health              │
│                           │  │                       │
│  Pinia (auth/theme)       │  │  SQLAlchemy 2.0 async │
│  Vue Router (guards)       │  │  Pydantic v2          │
│  Tailwind CSS              │  │  python-jose (JWT)    │
└──────────────┬──────────┘  └───────┬──────────────┘
               │                      │
        ┌──────▼──────────────────────▼──────┐
        │            Docker Compose            │
        │                                      │
        │  ┌──────────┐    ┌──────────┐       │
        │  │PostgreSQL│    │  Redis 7 │       │
        │  │ 16+vector│    │          │       │
        │  └──────────┘    └──────────┘       │
        └──────────────────────────────────────┘
```

**Data Flow — RAG Chat:**

```
User Question → POST /api/v1/ai/chat/stream
  → pgvector cosine distance search (top-K chunks)
  → pg_trgm keyword search (supplementary)
  → RRF reciprocal rank fusion
  → Build context from matched chunks
  → DeepSeek V4 Flash (SSE streaming)
  → Token-by-token response to browser
```

---

## Tech Stack

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
| | python-jose | JWT token generation & verification |
| | passlib + bcrypt | Password hashing |
| **Database** | PostgreSQL 16 | Primary data store |
| | pgvector | Vector embeddings for semantic search |
| | pg_trgm | Trigram fuzzy matching for search |
| **Cache** | Redis 7 | API caching, rate limiting, sorted sets, session storage |
| **AI** | DeepSeek V4 Flash | LLM for RAG chat & summarization |
| | OpenAI Embeddings | Text → 1536-dimension vector |
| **Infra** | Docker Compose | PostgreSQL + Redis containers |
| | Vite | Dev server with HMR & API proxy |
| | Uvicorn | ASGI server |

---

## Why This Stack

A few deliberate design choices worth explaining:

**Why Vue 3 + FastAPI (not Next.js or Nuxt)?**

Personal blog, not SSR-dependent content. A pure SPA + REST API separation gives cleaner boundaries, easier debugging, and more transferable skills — the same patterns apply to any frontend/backend split.

**Why DeepSeek V4 Flash for chat but OpenAI for embeddings?**

DeepSeek doesn't provide an embeddings API. The chat model is OpenAI-compatible, so swapping between providers only requires changing environment variables — no code changes. See `config.py` for the separation.

**Why PostgreSQL + pgvector instead of a dedicated vector DB?**

For a personal blog with hundreds (not millions) of documents, pgvector is more than sufficient. No additional infrastructure — one database for both structured data and vectors. The hybrid search (vector + trigram) outperforms pure vector search for this scale.

**Why Redis sorted sets for analytics?**

Page view counts need fast increment operations. Redis `ZINCRBY` is O(log N) and atomic — no race conditions. The `increment_view_count` function uses `post.view_count += 1` on the ORM object, and Redis tracks popularity ranking separately.

**Why CSS-animated ConfirmDialog instead of a UI library?**

Zero runtime dependencies beyond Vue itself. The dialogs, toasts, transitions, and layout components total under 400 lines of code and are fully typed. No lock-in to a third-party design system.

**Why two layout components instead of a single app shell?**

`PublicLayout.vue` (Header + Footer + AiChat) and `AdminLayout.vue` (Sidebar + TopBar + Breadcrumbs) are completely independent. Admin pages don't load the public Header or AI chat widget. Clean separation without a router meta hack.

---

## Project Structure

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
│   │   │   │   ├── public/         # Home, Post, Tags, TagPosts, Search, About, NotFound
│   │   │   │   └── admin/          # Dashboard, PostList, PostEditor, CommentList, MediaManager
│   │   │   ├── router/             # Route definitions + guards + 404
│   │   │   ├── services/           # SEO meta + JSON-LD
│   │   │   ├── stores/             # auth (Pinia), theme (Pinia)
│   │   │   ├── tracking/           # Client-side analytics with sendBeacon
│   │   │   ├── types/              # TypeScript interfaces
│   │   │   └── utils/              # constants.ts (SITE_NAME, API keys, etc.)
│   │   ├── index.html
│   │   ├── vite.config.ts          # Proxy /api → :8000, chunk splitting
│   │   └── tailwind.config.js
│   │
│   └── server/                     # FastAPI Backend
│       ├── app/
│       │   ├── api/v1/             # Route modules (posts, comments, auth, ai, rss, analytics)
│       │   ├── core/               # config, database, redis, security
│       │   ├── middleware/         # Telemetry middleware
│       │   ├── models/             # SQLAlchemy ORM: Post, Tag, Comment, User, Media, Analytics
│       │   ├── schemas/            # Pydantic request/response models
│       │   ├── services/           # Business logic: post, comment, ai, rag, cache, analytics
│       │   └── utils/              # Exceptions, pagination helpers
│       ├── alembic/                # Database migrations
│       ├── alembic.ini
│       └── requirements.txt
```

---

## Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 20+
- **Docker Desktop** (for PostgreSQL & Redis)

### 1. Start Infrastructure

```bash
docker compose up -d
```

PostgreSQL (port 5432) and Redis (port 6379) will start with health checks.

### 2. Configure Environment

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | DeepSeek API key for AI chat | *required* |
| `OPENAI_BASE_URL` | DeepSeek API endpoint | `https://api.deepseek.com` |
| `OPENAI_MODEL` | LLM model name | `deepseek-v4-flash` |
| `EMBEDDING_API_KEY` | OpenAI API key for embeddings | *required* |
| `EMBEDDING_BASE_URL` | OpenAI embedding endpoint | `https://api.openai.com/v1` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `SITE_URL` | Public site URL (for RSS) | `http://localhost:5173` |
| `SITE_NAME` | Blog name | `My Blog` |
| `JWT_SECRET_KEY` | JWT signing key | *change me* |
| `ADMIN_USERNAME` | Admin login | `admin` |
| `ADMIN_PASSWORD` | Admin password | `admin123` |

### 3. Install & Run Backend

```bash
cd apps/server
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: http://localhost:8000/docs

### 4. Install & Run Frontend

```bash
cd apps/web
npm install
npm run dev
```

Frontend: http://localhost:5173

### 5. Initialize Database

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
    print('Tables created')

asyncio.run(init())
"
```

Create admin user:

```bash
python -c "
import asyncio
from app.models.user import User
from app.core.security import hash_password
from app.core.database import async_session
from sqlalchemy import select

async def seed():
    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == 'admin'))
        if not result.scalar_one_or_none():
            session.add(User(username='admin', password_hash=hash_password('admin123')))
            await session.commit()
    print('Admin user created')

asyncio.run(seed())
"
```

### 6. Open

| URL | Page |
|-----|------|
| http://localhost:5173 | Blog Home |
| http://localhost:5173/admin | Admin Dashboard |
| http://localhost:5173/admin/posts/new | Write a Post |
| http://localhost:8000/docs | API Docs (Swagger) |
| http://localhost:8000/health | Health Check |

Default credentials: `admin` / `admin123`

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v1/posts` | — | Paginated post list (`?page=1&size=10&tag=frontend`) |
| `GET` | `/api/v1/posts/search?q=keyword` | — | Full-text search |
| `GET` | `/api/v1/posts/{slug}` | — | Post detail with tags + adjacent posts |
| `GET` | `/api/v1/posts/{slug}/summary` | — | AI-generated summary (7-day Redis cache) |
| `GET` | `/api/v1/tags` | — | All tags with post counts |
| `GET` | `/api/v1/tags/{slug}/posts` | — | Posts by tag |
| `POST` | `/api/v1/comments` | — | Submit comment (rate limited: 3/min/IP) |
| `GET` | `/api/v1/comments/{post_id}` | — | Approved comments for a post |
| `POST` | `/api/v1/ai/chat` | — | Non-streaming RAG chat |
| `POST` | `/api/v1/ai/chat/stream` | — | Streaming RAG chat (SSE) |
| `GET` | `/api/v1/rss` | — | RSS 2.0 feed (1-hour Redis cache) |
| `POST` | `/api/v1/auth/login` | — | Admin login (rate limited: 5/min/IP) |
| `GET` | `/api/v1/admin/posts` | Bearer | Admin post list with drafts |
| `POST` | `/api/v1/admin/posts` | Bearer | Create post |
| `PUT` | `/api/v1/admin/posts/{id}` | Bearer | Update post |
| `DELETE` | `/api/v1/admin/posts/{id}` | Bearer | Delete post |
| `POST` | `/api/v1/admin/media/upload` | Bearer | Upload media file |
| `GET` | `/api/v1/admin/comments/pending` | Bearer | Pending comments |
| `PUT` | `/api/v1/admin/comments/{id}/approve` | Bearer | Approve comment |
| `GET` | `/api/v1/admin/analytics/overview` | Bearer | Dashboard analytics |
| `GET` | `/health` | — | Health check (Redis + DB ping) |

---

## Security

- **JWT authentication** with configurable expiration (default 24h)
- **Password hashing** via bcrypt (passlib)
- **Rate limiting** on login (5/min/IP) and comments (3/min/IP)
- **File upload validation** — extension + MIME type double-check
- **IP hashing** for rate limit keys (SHA-256, not storing raw IPs)
- **CORS whitelist** — only configured origins can access the API
- **`.env` git-ignored** — no secrets in version control
- **Response interceptor** — 401 auto-redirects to login, clears token

---

## Roadmap

- [ ] GitHub Actions CI — lint + type-check + build
- [ ] pytest test suite — API integration tests
- [ ] vitest component tests — critical UI paths
- [ ] Docker production image — single `docker compose up` for full stack
- [ ] ESLint + Prettier — code style enforcement
- [ ] Draft auto-save — localStorage recovery in PostEditor
- [ ] Image paste/drag-drop — clipboard paste in Markdown editor
- [ ] i18n — English/Chinese toggle

---

## License

MIT
