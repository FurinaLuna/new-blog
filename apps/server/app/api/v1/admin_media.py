import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.dependencies import get_current_user
from app.schemas.common import PaginatedResponse
from app.services import media_service
from app.utils.sanitizers import sanitize_filename

settings = get_settings()
router = APIRouter(prefix="/admin", tags=["admin-media"])

MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"GIF8": "image/gif",
    b"RIFF": "image/webp",
    b"%PDF": "application/pdf",
    b"\x00\x00\x00": "video/mp4",
    b"\x1aE\xdf": "video/mp4",
}

MIME_TO_EXT = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/gif": {".gif"},
    "image/webp": {".webp"},
    "application/pdf": {".pdf"},
    "video/mp4": {".mp4"},
}

BLOCKED_EXTENSIONS = {".svg"}


def _detect_mime(content: bytes) -> str | None:
    for magic, mime in MAGIC_BYTES.items():
        if content[:len(magic)] == magic:
            return mime
    return None


def _check_path_traversal(filepath: str) -> None:
    real = os.path.realpath(filepath)
    base = os.path.realpath(settings.upload_dir)
    if not real.startswith(base + os.sep) and real != base:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="非法文件路径")


@router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    if file.size and file.size > settings.max_upload_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="文件过大")

    raw_filename = file.filename or "unknown"
    ext = os.path.splitext(raw_filename)[1].lower()

    if ext in BLOCKED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不允许上传SVG文件")

    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".mp4"}
    if ext not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件类型")

    content_type = file.content_type or ""
    allowed_mime_prefixes = ("image/", "application/pdf", "video/mp4")
    if not any(content_type.startswith(prefix) for prefix in allowed_mime_prefixes):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件类型")

    content = await file.read()

    detected_mime = _detect_mime(content)
    if detected_mime is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法验证文件实际类型")
    allowed_exts = MIME_TO_EXT.get(detected_mime, set())
    if ext not in allowed_exts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件实际类型与声明类型不一致")

    safe_name = sanitize_filename(raw_filename)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_path = os.path.join(settings.upload_dir, unique_name)

    _check_path_traversal(upload_path)

    os.makedirs(settings.upload_dir, exist_ok=True)
    with open(upload_path, "wb") as f:
        f.write(content)

    media = await media_service.save_media(
        db=db,
        filename=safe_name,
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
