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

settings = get_settings()
router = APIRouter(tags=["rss"])


@router.get("")
async def rss_feed(db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    cache_key = "cache:rss:feed"
    cached = await redis.get(cache_key)
    if cached:
        return Response(content=cached, media_type="application/rss+xml")

    posts_result = await ps.get_post_list(db, page=1, size=20)
    posts = posts_result.items

    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = settings.site_name
    SubElement(channel, "link").text = settings.site_url
    SubElement(channel, "description").text = settings.site_description

    for post in posts:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = post.title
        SubElement(item, "link").text = f"{settings.site_url}/post/{post.slug}"
        SubElement(item, "description").text = post.excerpt or post.content[:200]
        SubElement(item, "pubDate").text = post.created_at.replace(tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        SubElement(item, "guid").text = str(post.id)

    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(rss, encoding="unicode")
    await redis.setex(cache_key, 3600, xml_str)
    return Response(content=xml_str, media_type="application/rss+xml")
