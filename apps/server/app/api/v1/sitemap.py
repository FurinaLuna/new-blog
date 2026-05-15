from datetime import timezone
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from xml.etree.ElementTree import Element, SubElement, tostring

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import get_settings
from app.services import post_service as ps
from app.services import tag_service

settings = get_settings()
router = APIRouter(tags=["sitemap"])


@router.get("/sitemap.xml")
async def sitemap(db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    cache_key = "cache:sitemap:xml"
    cached = await redis.get(cache_key)
    if cached:
        return Response(content=cached, media_type="application/xml")

    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    home = SubElement(urlset, "url")
    SubElement(home, "loc").text = settings.site_url
    SubElement(home, "changefreq").text = "daily"
    SubElement(home, "priority").text = "1.0"

    about = SubElement(urlset, "url")
    SubElement(about, "loc").text = f"{settings.site_url}/about"
    SubElement(about, "changefreq").text = "monthly"
    SubElement(about, "priority").text = "0.5"

    tags_page = SubElement(urlset, "url")
    SubElement(tags_page, "loc").text = f"{settings.site_url}/tags"
    SubElement(tags_page, "changefreq").text = "weekly"
    SubElement(tags_page, "priority").text = "0.6"

    tags = await tag_service.get_all_tags(db)
    for tag in tags:
        tag_url = SubElement(urlset, "url")
        SubElement(tag_url, "loc").text = f"{settings.site_url}/tag/{tag.slug}"
        SubElement(tag_url, "changefreq").text = "weekly"
        SubElement(tag_url, "priority").text = "0.6"

    posts_result = await ps.get_post_list(db, page=1, size=1000)
    for post in posts_result.items:
        post_url = SubElement(urlset, "url")
        SubElement(post_url, "loc").text = f"{settings.site_url}/post/{post.slug}"
        if hasattr(post, "updated_at") and post.updated_at:
            SubElement(post_url, "lastmod").text = post.updated_at.replace(tzinfo=timezone.utc).strftime("%Y-%m-%d")
        SubElement(post_url, "changefreq").text = "monthly"
        SubElement(post_url, "priority").text = "0.8"

    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(urlset, encoding="unicode")
    await redis.setex(cache_key, 3600, xml_str)
    return Response(content=xml_str, media_type="application/xml")
