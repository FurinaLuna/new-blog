from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from app.utils.sanitizers import validate_slug


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
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=10)
    excerpt: str | None = None
    cover_image: str | None = None
    published: bool = False
    featured: bool = False
    tag_ids: list[str] = []

    @field_validator("slug")
    @classmethod
    def validate_slug_field(cls, v: str) -> str:
        validate_slug(v)
        return v

    @model_validator(mode="after")
    def validate_model(self):
        if self.excerpt is not None and len(self.excerpt) > 500:
            raise ValueError("摘要不能超过500个字符")
        return self


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    slug: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, min_length=10)
    excerpt: str | None = None
    cover_image: str | None = None
    published: bool | None = None
    featured: bool | None = None
    tag_ids: list[str] | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug_field(cls, v: str | None) -> str | None:
        if v is not None:
            validate_slug(v)
        return v

    @model_validator(mode="after")
    def validate_model(self):
        if self.excerpt is not None and len(self.excerpt) > 500:
            raise ValueError("摘要不能超过500个字符")
        return self

