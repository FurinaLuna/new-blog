from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.schemas.comment import CommentOut, BatchActionRequest
from app.services import comment_service

router = APIRouter(prefix="/admin", tags=["admin-comments"])


@router.get("/comments/pending", response_model=list[CommentOut])
async def pending_comments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    comments = await comment_service.get_pending_comments(db, page, size)
    return [CommentOut.model_validate(c) for c in comments]


@router.put("/comments/{comment_id}/approve", response_model=CommentOut)
async def approve_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    comment = await comment_service.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    comment = await comment_service.approve_comment(db, comment)
    return CommentOut.model_validate(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    comment = await comment_service.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    await comment_service.delete_comment(db, comment)


@router.post("/comments/batch-approve")
async def batch_approve_comments(
    data: BatchActionRequest,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    approved = []
    failed = []
    for cid in data.ids:
        try:
            async with db.begin_nested():
                comment = await comment_service.get_comment_by_id(db, cid)
                if comment:
                    comment = await comment_service.approve_comment(db, comment)
                    approved.append(CommentOut.model_validate(comment))
                else:
                    failed.append({"id": cid, "reason": "评论不存在"})
        except Exception:
            failed.append({"id": cid, "reason": "处理失败"})
    return {"approved": approved, "count": len(approved), "failed": failed}


@router.post("/comments/batch-delete")
async def batch_delete_comments(
    data: BatchActionRequest,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    deleted = 0
    failed = []
    for cid in data.ids:
        try:
            async with db.begin_nested():
                comment = await comment_service.get_comment_by_id(db, cid)
                if comment:
                    await comment_service.delete_comment(db, comment)
                    deleted += 1
                else:
                    failed.append({"id": cid, "reason": "评论不存在"})
        except Exception:
            failed.append({"id": cid, "reason": "处理失败"})
    return {"deleted": deleted, "failed": failed}
