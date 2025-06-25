import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import nats
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Notification, NotificationSubscription
from schemas import SubscriptionCreate, SubscriptionResponse, NotificationResponse, SubscriptionCheckResponse

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment variables
POSTGRES_URL = os.environ.get("POSTGRES_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/notification_db")
NATS_URL = os.environ.get("NATS_URL", "nats://nats:4222")

# FastAPI app
app = FastAPI(title="Notification Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_async_engine(POSTGRES_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Global NATS connection
nc = None
js = None

# Utility functions for hierarchical paths
def create_path(*components):
    """Create a standardized path from components"""
    # Remove any slashes from individual components to prevent path injection
    clean_components = [str(c).replace('/', '_') for c in components if c]
    return '/' + '/'.join(clean_components)

def get_parent_paths(path):
    """Get all parent paths in order from most specific to most general"""
    if not path or path == '/':
        return []
    
    # Ensure path starts with / and doesn't end with /
    norm_path = path if path.startswith('/') else '/' + path
    norm_path = norm_path[:-1] if norm_path.endswith('/') and len(norm_path) > 1 else norm_path
    
    parts = norm_path.split('/')
    parent_paths = []
    
    # Generate all parent paths
    for i in range(len(parts) - 1, 0, -1):
        parent_path = '/'.join(parts[:i])
        if not parent_path:
            parent_path = '/'
        parent_paths.append(parent_path)
    
    return parent_paths

def is_child_path(parent_path, child_path):
    """Check if child_path is a descendant of parent_path"""
    # Normalize paths
    norm_parent = parent_path if parent_path.startswith('/') else '/' + parent_path
    norm_parent = norm_parent if norm_parent.endswith('/') else norm_parent + '/'
    
    norm_child = child_path if child_path.startswith('/') else '/' + child_path
    norm_child = norm_child + '/' if not norm_child.endswith('/') and norm_child != '/' else norm_child
    
    return norm_child.startswith(norm_parent) and norm_child != norm_parent

# Database dependency
async def get_db():
    async with async_session() as session:
        yield session

# Simulate auth for demo
async def get_current_user_id():
    # In a real app, you'd extract this from the auth token
    return "user123"

# API routes
@app.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    user_id: str = Depends(get_current_user_id),
    path: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    is_read: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(50, gt=0, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get notifications for a user with optional filtering"""
    query = (
        select(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.timestamp.desc())
    )
    
    # Apply filters
    if path:
        query = query.filter(Notification.object_path == path)
    if event_type:
        query = query.filter(Notification.type == event_type)
    if severity:
        query = query.filter(Notification.severity == severity)
    if from_date:
        query = query.filter(Notification.timestamp >= from_date)
    if to_date:
        query = query.filter(Notification.timestamp <= to_date)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    if search:
        query = query.filter(
            or_(
                Notification.title.ilike(f"%{search}%"),
                Notification.content.ilike(f"%{search}%"),
            )
        )
    
    # Execute query with pagination
    result = await db.execute(query.offset(offset).limit(limit))
    return result.scalars().all()

@app.post("/notifications/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read"""
    result = await db.execute(
        select(Notification).filter(
            Notification.id == notification_id, 
            Notification.user_id == user_id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    await db.commit()
    
    return {"status": "success"}

@app.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new subscription for a hierarchical path"""
    # Normalize the path
    path = subscription.path if subscription.path.startswith('/') else '/' + subscription.path
    
    # Check if subscription already exists
    result = await db.execute(
        select(NotificationSubscription).filter(
            NotificationSubscription.user_id == user_id,
            NotificationSubscription.path == path
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing
        existing.include_children = subscription.include_children
        existing.notification_types = subscription.notification_types
        existing.settings = subscription.settings
        await db.commit()
        return existing
    
    # Create new
    new_subscription = NotificationSubscription(
        id=str(uuid.uuid4()),
        user_id=user_id,
        path=path,
        include_children=subscription.include_children,
        notification_types=subscription.notification_types,
        settings=subscription.settings,
    )
    
    db.add(new_subscription)
    await db.commit()
    
    return new_subscription

@app.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    user_id: str = Depends(get_current_user_id),
    path_prefix: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all subscriptions for a user, optionally filtered by path prefix"""
    query = select(NotificationSubscription).filter(
        NotificationSubscription.user_id == user_id
    )
    
    if path_prefix:
        query = query.filter(NotificationSubscription.path.startswith(path_prefix))
    
    result = await db.execute(query.order_by(NotificationSubscription.path))
    return result.scalars().all()

@app.delete("/subscriptions/{subscription_id}")
async def delete_subscription(
    subscription_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a subscription"""
    result = await db.execute(
        select(NotificationSubscription).filter(
            NotificationSubscription.id == subscription_id,
            NotificationSubscription.user_id == user_id
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    try:
        # First, update all notifications to remove the foreign key reference
        update_result = await db.execute(
            update(Notification)
            .where(Notification.subscription_id == subscription_id)
            .values(subscription_id=None)
        )
        
        # Flush to ensure the update is applied before delete
        await db.flush()
        
        logger.info(f"Updated {update_result.rowcount} notifications for subscription {subscription_id}")
        
        # Now we can safely delete the subscription
        await db.delete(subscription)
        await db.commit()
        
        logger.info(f"Successfully deleted subscription {subscription_id}")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error deleting subscription {subscription_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete subscription: {str(e)}")

@app.get("/subscriptions/check", response_model=SubscriptionCheckResponse)
async def check_subscription(
    path: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Check if a user is subscribed to a path or any of its parent paths"""
    # Normalize path
    normalized_path = path if path.startswith('/') else '/' + path
    
    # Get all parent paths
    parent_paths = get_parent_paths(normalized_path)
    all_paths = [normalized_path] + parent_paths
    
    # Check direct subscription
    result = await db.execute(
        select(NotificationSubscription).filter(
            NotificationSubscription.user_id == user_id,
            NotificationSubscription.path == normalized_path
        )
    )
    direct_sub = result.scalar_one_or_none()
    
    # Check inherited subscription (from parent with include_children=True)
    parent_sub = None
    if parent_paths:
        result = await db.execute(
            select(NotificationSubscription).filter(
                NotificationSubscription.user_id == user_id,
                NotificationSubscription.path.in_(parent_paths),
                NotificationSubscription.include_children == True
            ).order_by(func.length(NotificationSubscription.path).desc())
        )
        parent_sub = result.scalar_one_or_none()
    
    return {
        "path": normalized_path,
        "is_subscribed": direct_sub is not None or parent_sub is not None,
        "direct_subscription": direct_sub,
        "inherited_subscription": parent_sub
    }

# NATS event processing
async def process_event(msg):
    """Process events from NATS and create notifications for subscribed users"""
    try:
        payload = json.loads(msg.data.decode())
        logger.info(f"Processing event: {msg.subject}")
        
        # Extract event details
        object_path = payload.get("object_path")
        event_type = payload.get("event_type")
        
        if not object_path or not event_type:
            logger.error(f"Invalid event payload: {payload}")
            return
        
        # Normalize path
        normalized_path = object_path if object_path.startswith('/') else '/' + object_path
        
        # Get all parent paths
        parent_paths = get_parent_paths(normalized_path)
        all_paths = [normalized_path] + parent_paths
        
        async with async_session() as db:
            # Find direct subscriptions
            result = await db.execute(
                select(NotificationSubscription).filter(
                    NotificationSubscription.path == normalized_path
                )
            )
            direct_subs = result.scalars().all()
            
            # Find parent subscriptions with include_children=True
            parent_subs = []
            if parent_paths:
                result = await db.execute(
                    select(NotificationSubscription).filter(
                        NotificationSubscription.path.in_(parent_paths),
                        NotificationSubscription.include_children == True
                    )
                )
                parent_subs = result.scalars().all()
            
            # Combine and deduplicate subscribers
            subscribed_users = {}  # user_id -> subscription
            
            for sub in direct_subs:
                subscribed_users[sub.user_id] = sub
                
            for sub in parent_subs:
                if sub.user_id not in subscribed_users:
                    subscribed_users[sub.user_id] = sub
            
            # Process notifications for each subscriber
            for user_id, subscription in subscribed_users.items():
                # Check if this event type is in allowed types
                if (subscription.notification_types and 
                    event_type not in subscription.notification_types):
                    continue
                
                # Create notification
                notification = Notification(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    type=event_type,
                    title=generate_title(normalized_path, event_type),
                    content=generate_content(normalized_path, event_type, payload),
                    severity=get_severity(event_type),
                    timestamp=datetime.now(),
                    is_read=False,
                    object_path=normalized_path,
                    action_url=generate_action_url(normalized_path),
                    subscription_id=subscription.id,
                    inherited=subscription.path != normalized_path,
                    extra_data={
                        "object_path": normalized_path,
                        "subscription_path": subscription.path,
                        "source_event": msg.subject,
                        "payload": payload
                    }
                )
                
                db.add(notification)
                
                # Also publish to user's notification channel for real-time updates
                notification_data = notification.to_dict()
                await nc.publish(
                    f"notification.user.{user_id}",
                    json.dumps(notification_data).encode()
                )
            
            # Create a system-level notification for debugging/monitoring purposes
            # This allows the System Log to show ALL events, regardless of subscriptions
            system_notification = Notification(
                id=str(uuid.uuid4()),
                user_id="system",  # Special system user for monitoring
                type=event_type,
                title=generate_title(normalized_path, event_type),
                content=generate_content(normalized_path, event_type, payload),
                severity=get_severity(event_type),
                timestamp=datetime.now(),
                is_read=False,
                object_path=normalized_path,
                action_url=generate_action_url(normalized_path),
                subscription_id=None,  # No subscription for system notifications
                inherited=False,
                extra_data={
                    "object_path": normalized_path,
                    "source_event": msg.subject,
                    "payload": payload,
                    "system_event": True  # Mark as system event for filtering
                }
            )
            
            db.add(system_notification)
            
            await db.commit()
                
    except Exception as e:
        logger.exception(f"Error processing event: {e}")

def generate_title(path, event_type):
    """Generate a title for a notification based on path and event type"""
    # Extract object name from path
    parts = path.strip('/').split('/')
    object_name = parts[-1] if parts else "item"
    
    # Capitalize and format for display
    object_display = object_name.replace('-', ' ').replace('_', ' ').title()
    
    if event_type == "created":
        return f"New {object_display} created"
    elif event_type == "updated":
        return f"{object_display} was updated"
    elif event_type == "deleted":
        return f"{object_display} was deleted"
    elif event_type == "commented":
        return f"New comment on {object_display}"
    else:
        return f"{event_type.replace('_', ' ').title()} on {object_display}"

def generate_content(path, event_type, payload):
    """Generate content for a notification"""
    # Extract object name from path
    parts = path.strip('/').split('/')
    object_name = parts[-1] if parts else "item"
    object_display = object_name.replace('-', ' ').replace('_', ' ').title()
    
    # Get data from payload
    data = payload.get("data", {})
    user_name = data.get("user_name", "Someone")
    
    if event_type == "created":
        return f"{user_name} created a new {object_display}"
    elif event_type == "updated":
        return f"{user_name} updated {object_display}"
    elif event_type == "deleted":
        return f"{user_name} deleted {object_display}"
    elif event_type == "commented":
        comment = data.get("comment", "")
        return f"{user_name} commented on {object_display}: \"{comment}\""
    else:
        return f"{user_name} performed {event_type.replace('_', ' ')} on {object_display}"

def get_severity(event_type):
    """Map event types to severity levels"""
    severity_map = {
        "created": "info",
        "updated": "info",
        "deleted": "warning",
        "commented": "info",
        "error": "error",
        "warning": "warning",
        "alert": "critical",
    }
    return severity_map.get(event_type, "info")

def generate_action_url(path):
    """Generate a URL for the notification action"""
    # In a real app, this would map to your frontend routes
    return f"/app{path}"

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database and NATS connection on startup"""
    global nc, js
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Connect to NATS
    try:
        nc = await nats.connect(NATS_URL)
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
        
        # Subscribe to application events
        await nc.subscribe("app.events.>", cb=process_event)
        logger.info("Subscribed to application events")
        
    except Exception as e:
        logger.error(f"Failed to connect to NATS: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown"""
    if nc:
        await nc.close()
    
    await engine.dispose()

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/system/notifications", response_model=List[NotificationResponse])
async def get_all_notifications(
    path: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    is_read: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(100, gt=0, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get all notifications in the system for monitoring purposes (no user filter)"""
    query = (
        select(Notification)
        .order_by(Notification.timestamp.desc())
    )
    
    # Apply filters
    if path:
        query = query.filter(Notification.object_path == path)
    if event_type:
        query = query.filter(Notification.type == event_type)
    if severity:
        query = query.filter(Notification.severity == severity)
    if from_date:
        query = query.filter(Notification.timestamp >= from_date)
    if to_date:
        query = query.filter(Notification.timestamp <= to_date)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Notification.title.ilike(search_pattern),
                Notification.content.ilike(search_pattern),
                Notification.object_path.ilike(search_pattern)
            )
        )
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
