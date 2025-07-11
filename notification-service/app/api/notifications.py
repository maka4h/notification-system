"""
API routes for notifications
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import NotificationResponse, BulkMarkAsReadRequest, BulkMarkAsReadResponse
from app.services import NotificationService
from app.core.dependencies import get_db, get_current_user_id

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get(
    "", 
    response_model=List[NotificationResponse],
    summary="Get user notifications",
    description="Retrieve notifications for the current user with comprehensive filtering options",
)
async def get_notifications(
    user_id: str = Depends(get_current_user_id),
    path: Optional[str] = Query(None, description="Filter by exact object path"),
    event_type: Optional[str] = Query(None, description="Filter by event type (created, updated, deleted, etc.)"),
    severity: Optional[str] = Query(None, description="Filter by severity level (info, warning, error, critical)"),
    from_date: Optional[datetime] = Query(None, description="Filter notifications from this date onwards"),
    to_date: Optional[datetime] = Query(None, description="Filter notifications up to this date"),
    is_read: Optional[bool] = Query(None, description="Filter by read status (true for read, false for unread)"),
    search: Optional[str] = Query(None, description="Search in notification title and content"),
    limit: int = Query(50, gt=0, le=200, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get notifications for the current user with optional filtering.
    
    This endpoint supports comprehensive filtering and pagination for user notifications.
    Notifications are returned in descending chronological order (newest first).
    """
    service = NotificationService(db)
    
    filters = {}
    if path:
        filters['path'] = path
    if event_type:
        filters['event_type'] = event_type
    if severity:
        filters['severity'] = severity
    if from_date:
        filters['from_date'] = from_date
    if to_date:
        filters['to_date'] = to_date
    if is_read is not None:
        filters['is_read'] = is_read
    if search:
        filters['search'] = search
    
    return await service.get_notifications(user_id, limit, offset, **filters)


@router.post(
    "/{notification_id}/read",
    summary="Mark notification as read",
    description="Mark a specific notification as read for the current user",
)
async def mark_as_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a specific notification as read.
    
    This endpoint marks a notification as read for the current user.
    The notification must belong to the current user, otherwise a 404 error is returned.
    """
    service = NotificationService(db)
    success = await service.mark_as_read(notification_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"status": "success"}


@router.post(
    "/bulk-read",
    response_model=BulkMarkAsReadResponse,
    summary="Mark multiple notifications as read",
    description="Mark multiple notifications as read in a single operation",
)
async def bulk_mark_as_read(
    request: BulkMarkAsReadRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark multiple notifications as read in a single operation.
    
    This endpoint allows marking multiple notifications as read at once,
    which is useful for "select all" and bulk operations in the UI.
    """
    service = NotificationService(db)
    
    try:
        return await service.bulk_mark_as_read(request, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
