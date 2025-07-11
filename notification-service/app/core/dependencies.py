"""
Dependency injection for the application
"""
from typing import Optional
from fastapi import Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_async_session


# Database dependency
async def get_db():
    async with get_async_session() as session:
        yield session


# Get user ID from query param or header (for demo purposes)
async def get_current_user_id(
    user_id: Optional[str] = Query(None, description="User ID for demo purposes"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Get current user ID from query parameter or header.
    In a real application, this would extract the user ID from authentication tokens.
    For demo purposes, we accept it from query params or headers.
    """
    # Priority: header first, then query param, then default
    if x_user_id:
        return x_user_id
    elif user_id:
        return user_id
    else:
        return "user123"  # Default user for backward compatibility
