"""
Test configuration and fixtures
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from datetime import datetime

from app.main import app
from app.core.dependencies import get_db
from models import Base, Notification
import os


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session") 
async def test_engine():
    """Create a test database engine using SQLite."""
    # Use in-memory SQLite for tests
    database_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(
        database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with AsyncSession(test_engine) as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""
    app.dependency_overrides[get_db] = lambda: test_db
    
    async with AsyncClient(base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_id() -> str:
    """Sample user ID for testing."""
    return "test-user-123"


@pytest.fixture
def sample_notification_data():
    """Sample notification data for testing."""
    return {
        "type": "task.completed",
        "title": "Task Completed",
        "content": "Your task has been completed successfully",
        "severity": "info",
        "object_path": "/projects/test-project/tasks/task-1",
        "user_id": "test-user-123",
        "action_url": "https://example.com/tasks/1"
    }


@pytest.fixture
def sample_subscription_data():
    """Sample subscription data for testing."""
    return {
        "path": "/projects/test-project",
        "include_children": True,
        "notification_types": ["task.completed", "task.failed"]
    }


@pytest.fixture
async def sample_notification(test_db, sample_notification_data):
    """Create a sample notification in the database."""
    notification = Notification(**sample_notification_data)
    test_db.add(notification)
    await test_db.commit()
    await test_db.refresh(notification)
    return notification
