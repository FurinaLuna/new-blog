from pydantic import BaseModel


class TagOut(BaseModel):
    id: str
    name: str
    slug: str
    post_count: int = 0

    model_config = {"from_attributes": True}


class TagCreate(BaseModel):
    name: str
    slug: str


class TagUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None


class TagAdminOut(TagOut):
    post_count: int = 0
