from datetime import datetime
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    post_id: str
    author: str = Field(min_length=1, max_length=100)
    email: str | None = None
    content: str = Field(min_length=1, max_length=5000)


class CommentOut(BaseModel):
    id: str
    post_id: str
    author: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
