import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class Settings:
    """Application settings"""
    
    # Database
    POSTGRES_URL: str = os.environ.get(
        "POSTGRES_URL", 
        "postgresql+asyncpg://postgres:postgres@postgres:5432/notification_db"
    )
    
    # NATS
    NATS_URL: str = os.environ.get("NATS_URL", "nats://nats:4222")
    
    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # Application
    APP_NAME: str = "Hierarchical Notification Service API"
    VERSION: str = "0.8.0"
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]  # Update for production
    
    # Authentication (for demo purposes)
    DEFAULT_USER_ID: str = "user123"

settings = Settings()

# Database setup
engine = create_async_engine(settings.POSTGRES_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def get_async_session():
    """Get async database session"""
    return async_session()
