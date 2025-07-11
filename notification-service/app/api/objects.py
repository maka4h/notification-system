"""
API routes for objects
"""
from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import SystemService
from app.core.dependencies import get_db

router = APIRouter(prefix="/objects", tags=["system"])


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
    
    **Response Structure:**
    - Array of root-level objects
    - Each object has `path` and `children` properties
    - Children are recursively structured in the same format
    - Paths are normalized and sorted alphabetically
    
    **Use Cases:**
    - Object Browser UI to display hierarchical structure
    - Understanding system topology
    - Subscription management interface
    
    **Data Sources:**
    - Unique paths from all notifications
    - Unique paths from all subscriptions
    - Automatically builds parent-child relationships
    """
    service = SystemService(db)
    return await service.get_object_hierarchy()
