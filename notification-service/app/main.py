"""
Main application entry point
"""
import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

import nats
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from models import Base
from app.core.config import settings, engine
from app.api.router import api_router
from app.services.event_processor import EventProcessor

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global NATS connection
nc = None
js = None
event_processor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global nc, js, event_processor
    
    # Startup
    logger.info("Starting up notification service...")
    
    # Run Alembic migrations to set up database schema and data
    import subprocess
    import os
    
    try:
        # Run Alembic upgrade to latest
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="/app",
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Database migrations completed successfully")
        logger.debug(f"Alembic output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Database migration failed: {e}")
        logger.error(f"Alembic stderr: {e.stderr}")
        logger.error(f"Alembic stdout: {e.stdout}")
        raise
    
    # Connect to NATS
    try:
        nc = await nats.connect(settings.NATS_URL)
        js = nc.jetstream()
        logger.info("Connected to NATS")
        
        # Ensure streams exist
        try:
            # For application events
            await js.add_stream(name="EVENTS", subjects=["app.events.>"])
            # For user notifications
            await js.add_stream(name="NOTIFICATIONS", subjects=["notification.>"])
        except Exception as e:
            logger.warning(f"Stream already exists or error: {e}")
        
        # Initialize event processor
        event_processor = EventProcessor(nc)
        
        # Subscribe to application events
        await nc.subscribe("app.events.>", cb=event_processor.process_event)
        logger.info("Subscribed to application events")
        
    except Exception as e:
        logger.error(f"Failed to connect to NATS: {e}")
    
    logger.info("Notification service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down notification service...")
    
    if nc:
        await nc.close()
    
    await engine.dispose()
    
    logger.info("Notification service shutdown complete")


# FastAPI app with comprehensive documentation
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## 🔔 Hierarchical Notification Service

    A comprehensive notification system that supports hierarchical object subscriptions and real-time notifications.

    ### Features

    * **Hierarchical Subscriptions**: Subscribe to objects at any level in a hierarchy and automatically receive notifications for child objects
    * **Real-time Notifications**: WebSocket-based real-time notification delivery  
    * **Persistent Storage**: All notifications are stored in PostgreSQL for historical access
    * **Flexible Filtering**: Filter notifications by severity, event type, read status, date range, and object path
    * **Configuration Management**: Backend-driven configuration for severity levels, event types, and UI settings
    * **NATS Integration**: Uses NATS JetStream for reliable message delivery and event streaming

    ### API Organization

    The API is organized into the following sections:
    
    * **Subscriptions**: Manage notification subscriptions for hierarchical objects
    * **Notifications**: Retrieve, mark as read, and manage notifications
    * **Configuration**: Get system configuration for UI components and filtering
    * **System**: Health checks and object hierarchy management
    * **WebSocket**: Real-time notification streaming

    ### Authentication

    Currently, this API does not require authentication. In a production environment, 
    you would want to add proper authentication and authorization.
    """,
    version=settings.VERSION,
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Notification Service Team",
        "url": "https://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "subscriptions",
            "description": "Manage notification subscriptions for hierarchical objects. Subscribing to a parent object automatically includes notifications for all child objects.",
        },
        {
            "name": "notifications", 
            "description": "Retrieve, filter, and manage notifications. Includes bulk operations for marking notifications as read.",
        },
        {
            "name": "configuration",
            "description": "Get system configuration including available severity levels, event types, and UI settings.",
        },
        {
            "name": "system",
            "description": "System health checks and object hierarchy management.",
        },
        {
            "name": "websocket",
            "description": "Real-time notification streaming via WebSocket connections.",
        },
    ],
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Health check endpoint - duplicated here for easy access
@app.get("/health")
async def health():
    """Health check endpoint"""
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# WebSocket endpoint for real-time notifications
@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time notification streaming.
    
    This WebSocket endpoint provides real-time notification delivery to connected clients.
    When a user subscribes to this endpoint, they will receive notifications as they are created.
    """
    await websocket.accept()
    
    try:
        if nc:
            # Subscribe to user-specific notification channel
            sub = await nc.subscribe(f"notification.user.{user_id}")
            
            async def message_handler():
                try:
                    async for msg in sub.messages:
                        notification_data = json.loads(msg.data.decode())
                        await websocket.send_text(json.dumps(notification_data))
                except Exception as e:
                    logger.error(f"Error in WebSocket message handler: {e}")
                    return
            
            # Start message handling task
            task = asyncio.create_task(message_handler())
            
            # Keep connection alive
            while True:
                try:
                    await websocket.receive_text()
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"WebSocket error: {e}")
                    break
            
            # Cleanup
            task.cancel()
            await sub.unsubscribe()
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
