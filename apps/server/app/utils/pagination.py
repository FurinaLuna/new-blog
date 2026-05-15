from app.schemas.common import PaginatedResponse
from app.utils.serializers import post_to_dict


def build_paginated_response(items, total: int, page: int, size: int) -> PaginatedResponse:
    from app.schemas.post import PostListOut
    pages = (total + size - 1) // size if total > 0 else 0
    return PaginatedResponse[PostListOut](
        items=[PostListOut.model_validate(post_to_dict(p)) for p in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
