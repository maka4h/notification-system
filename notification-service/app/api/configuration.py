"""
API routes for configuration
"""
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import ConfigurationService
from app.core.dependencies import get_db

router = APIRouter(prefix="/config", tags=["configuration"])


@router.get(
    "/severity-levels",
    summary="Get severity levels configuration",
    description="Get available notification severity levels with their display configuration",
)
async def get_severity_levels(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get available notification severity levels with their display configuration.
    
    This endpoint provides the complete configuration for notification severity levels,
    including display labels, descriptions, Bootstrap CSS classes, and priority ordering.
    """
    service = ConfigurationService(db)
    return await service.get_severity_levels()


@router.get(
    "/event-types",
    summary="Get event types configuration", 
    description="Get available event types for filtering and subscription",
)
async def get_event_types(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get available event types for filtering and subscription.
    
    This endpoint provides the complete list of event types supported by the system,
    with display labels and descriptions.
    """
    service = ConfigurationService(db)
    return await service.get_event_types()


@router.get(
    "/ui",
    summary="Get UI configuration",
    description="Get UI configuration including help text and customizable content",
)
async def get_ui_config() -> Dict[str, Any]:
    """
    Get UI configuration including help text and customizable content.
    
    This endpoint provides configuration for frontend UI components,
    including help text, feature descriptions, and display settings.
    """
    return ConfigurationService.get_ui_config()
