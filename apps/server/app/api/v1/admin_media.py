import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.dependencies import get_current_user
from app.schemas.post import PaginatedResponse
from app.services import media_service

settings = get_settings()
router = APIRouter(prefix="/admin", tags=["admin-media"])


@router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    if file.size and file.size > settings.max_upload_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="文件过大")

    ext = os.path.splitext(file.filename or "file")[1].lower()
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".mp4"}
    if ext not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件类型")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_path = os.path.join(settings.upload_dir, unique_name)
    os.makedirs(settings.upload_dir, exist_ok=True)

    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)

    media = await media_service.save_media(
        db=db,
        filename=file.filename or "unknown",
        file_path=upload_path,
        mime_type=file.content_type or "application/octet-stream",
        size=len(content),
    )
    return {
        "id": media.id,
        "filename": media.filename,
        "url": media.url,
        "mime_type": media.mime_type,
        "size": media.size,
    }


@router.get("/media")
async def list_media(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    items, total = await media_service.get_all_media(db, page, size)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.delete("/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    media = await media_service.get_media_by_id(db, media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    if os.path.exists(media.file_path):
        os.remove(media.file_path)
    await media_service.delete_media(db, media)
