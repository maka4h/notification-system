"""
Dependency injection for the application
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_async_session


# Database dependency
async def get_db():
    async with get_async_session() as session:
        yield session


# Simulate auth for demo
async def get_current_user_id():
    # In a real app, you'd extract this from the auth token
    return "user123"
