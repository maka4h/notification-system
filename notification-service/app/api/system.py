"""
API routes for system operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import NotificationResponse
from app.services import SystemService
from app.core.dependencies import get_db

router = APIRouter(prefix="/system", tags=["system"])


@router.get(
    "/notifications", 
    response_model=List[NotificationResponse],
    summary="Get all system notifications",
    description="Retrieve all notifications in the system for monitoring and debugging purposes",
)
async def get_all_notifications(
    path: Optional[str] = Query(None, description="Filter by exact object path"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    from_date: Optional[datetime] = Query(None, description="Filter notifications from this date"),
    to_date: Optional[datetime] = Query(None, description="Filter notifications up to this date"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    search: Optional[str] = Query(None, description="Search in title, content, and object path"),
    limit: int = Query(100, gt=0, le=500, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all notifications in the system for monitoring and debugging purposes.
    
    This endpoint returns notifications for all users and is intended for system monitoring,
    debugging, and administrative purposes.
    """
    service = SystemService(db)
    
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
    
    return await service.get_all_notifications(limit, offset, **filters)


@router.get(
    "/hierarchy",
    summary="Get object hierarchy", 
    description="Get the hierarchical structure of all objects in the system",
)
async def get_object_hierarchy(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get the hierarchical structure of all objects in the system.
    
    This endpoint analyzes all notification and subscription paths to build
    a hierarchical tree structure of objects in the system.
    """
    service = SystemService(db)
    return await service.get_object_hierarchy()


@router.get(
    "/health",
    summary="Health check", 
    description="Check the health status of the notification service",
    include_in_schema=False  # Don't include in system endpoints since it's also at root
)
async def health() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.
    
    This endpoint provides a simple health check for the notification service.
    It returns a 200 status code with current timestamp when the service is operational.
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
