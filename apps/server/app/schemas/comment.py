import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr
from app.utils.sanitizers import strip_html_tags


class CommentCreate(BaseModel):
    post_id: str
    author: str = Field(min_length=1, max_length=50)
    email: EmailStr | None = None
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("author")
    @classmethod
    def validate_author(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("作者名不能为空")
        if re.match(r"^[\d\s\W]+$", v):
            raise ValueError("作者名不能只包含数字或特殊字符")
        return v

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        v = strip_html_tags(v)
        v = v.strip()
        if not v:
            raise ValueError("评论内容不能为空")
        return v


class CommentOut(BaseModel):
    id: str
    post_id: str
    author: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchActionRequest(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=50)
