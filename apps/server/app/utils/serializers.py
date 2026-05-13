"""Shared serialization helpers — single source of truth for model→dict conversion."""

from app.models.post import Post


def post_to_dict(p: Post) -> dict:
    """Convert a Post ORM object to a dict suitable for PostListOut validation."""
    return {
        "id": p.id,
        "title": p.title,
        "slug": p.slug,
        "excerpt": p.excerpt,
        "cover_image": p.cover_image,
        "published": p.published,
        "featured": p.featured,
        "view_count": p.view_count,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
        "tags": [
            {"id": pt.tag.id, "name": pt.tag.name, "slug": pt.tag.slug}
            for pt in (p.tags or [])
        ],
    }
