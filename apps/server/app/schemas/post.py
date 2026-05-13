from datetime import datetime
from pydantic import BaseModel


class TagBrief(BaseModel):
    id: str
    name: str
    slug: str

    model_config = {"from_attributes": True}


class PostListOut(BaseModel):
    id: str
    title: str
    slug: str
    excerpt: str | None
    cover_image: str | None
    featured: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagBrief]

    model_config = {"from_attributes": True}


class PostDetailOut(BaseModel):
    id: str
    title: str
    slug: str
    content: str
    excerpt: str | None
    cover_image: str | None
    featured: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagBrief]
    prev_post: "PostListOut | None" = None
    next_post: "PostListOut | None" = None

    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    title: str
    slug: str
    content: str
    excerpt: str | None = None
    cover_image: str | None = None
    published: bool = False
    featured: bool = False
    tag_ids: list[str] = []


class PostUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    content: str | None = None
    excerpt: str | None = None
    cover_image: str | None = None
    published: bool | None = None
    featured: bool | None = None
    tag_ids: list[str] | None = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int
