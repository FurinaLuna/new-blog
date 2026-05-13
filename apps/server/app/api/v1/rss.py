from datetime import timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from xml.etree.ElementTree import Element, SubElement, tostring

from app.core.database import get_db
from app.services import post_service as ps

router = APIRouter(tags=["rss"])


@router.get("")
async def rss_feed(db: AsyncSession = Depends(get_db)):
    posts_result = await ps.get_post_list(db, page=1, size=20)
    posts = posts_result.items

    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "My Blog"
    SubElement(channel, "link").text = "http://localhost:5173"
    SubElement(channel, "description").text = "Personal blog RSS feed"

    for post in posts:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = post.title
        SubElement(item, "link").text = f"http://localhost:5173/post/{post.slug}"
        SubElement(item, "description").text = post.excerpt or post.content[:200]
        SubElement(item, "pubDate").text = post.created_at.replace(tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        SubElement(item, "guid").text = str(post.id)

    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(rss, encoding="unicode")

    from fastapi.responses import Response
    return Response(content=xml_str, media_type="application/rss+xml")
