"""
Legacy main.py - now imports from the clean architecture
"""
from app.main import app

# For backward compatibility, we expose the app here
__all__ = ["app"]

# API routes
@app.get(
    "/notifications", 
    response_model=List[NotificationResponse],
    tags=["notifications"],
    summary="Get user notifications",
    description="Retrieve notifications for the current user with comprehensive filtering options",
    responses={
        200: {
            "description": "List of notifications matching the filter criteria",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "type": "created",
                            "title": "New Project Alpha created",
                            "content": "John Doe created a new Project Alpha",
                            "severity": "info",
                            "timestamp": "2024-01-15T10:30:00Z",
                            "is_read": False,
                            "object_path": "/projects/alpha",
                            "action_url": "/app/projects/alpha"
                        }
                    ]
                }
            }
        }
    }
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
    
    **Filter Parameters:**
    - `path`: Exact object path match
    - `event_type`: Filter by specific event types
    - `severity`: Filter by severity levels
    - `from_date`/`to_date`: Date range filtering
    - `is_read`: Filter by read status
    - `search`: Full-text search in title and content
    
    **Pagination:**
    - Use `limit` and `offset` for pagination
    - Maximum limit is 200 notifications per request
    """
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

@app.post(
    "/notifications/{notification_id}/read",
    tags=["notifications"],
    summary="Mark notification as read",
    description="Mark a specific notification as read for the current user",
    responses={
        200: {
            "description": "Notification successfully marked as read",
            "content": {
                "application/json": {
                    "example": {"status": "success"}
                }
            }
        },
        404: {
            "description": "Notification not found or doesn't belong to current user"
        }
    }
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
    
    **Path Parameters:**
    - `notification_id`: UUID of the notification to mark as read
    """
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

@app.post(
    "/notifications/bulk-read",
    response_model=BulkMarkAsReadResponse,
    tags=["notifications"],
    summary="Mark multiple notifications as read",
    description="Mark multiple notifications as read in a single operation",
    responses={
        200: {
            "description": "Bulk operation completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "updated_count": 5,
                        "message": "5 notifications marked as read"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request - no notification IDs provided"
        }
    }
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
    
    **Request Body:**
    - `notification_ids`: Array of notification UUIDs to mark as read
    
    **Behavior:**
    - Only notifications belonging to the current user are updated
    - Invalid or non-existent notification IDs are silently ignored
    - Returns the count of successfully updated notifications
    
    **Response:**
    - `status`: "success" if operation completed
    - `updated_count`: Number of notifications actually updated
    - `message`: Human-readable status message
    """
    if not request.notification_ids:
        raise HTTPException(status_code=400, detail="No notification IDs provided")
    
    # Update notifications that belong to the current user
    result = await db.execute(
        update(Notification)
        .where(
            and_(
                Notification.id.in_(request.notification_ids),
                Notification.user_id == user_id,
                Notification.is_read == False  # Only update unread notifications
            )
        )
        .values(is_read=True)
    )
    
    await db.commit()
    
    updated_count = result.rowcount
    
    return BulkMarkAsReadResponse(
        status="success",
        updated_count=updated_count,
        message=f"{updated_count} notifications marked as read"
    )

@app.post(
    "/subscriptions", 
    response_model=SubscriptionResponse,
    tags=["subscriptions"],
    summary="Create notification subscription",
    description="Create a new notification subscription for a hierarchical object path",
    responses={
        200: {
            "description": "Subscription created or updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "user123",
                        "path": "/projects/alpha",
                        "include_children": True,
                        "notification_types": ["created", "updated", "deleted"],
                        "settings": {"email": True, "push": False}
                    }
                }
            }
        }
    }
)
async def create_subscription(
    subscription: SubscriptionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new notification subscription for a hierarchical object path.
    
    This endpoint creates a new subscription or updates an existing one for the same path.
    When `include_children` is true, the subscription will also receive notifications
    for all child objects in the hierarchy.
    
    **Request Body:**
    - `path`: The object path to subscribe to (e.g., "/projects/alpha")
    - `include_children`: Whether to include notifications for child objects
    - `notification_types`: List of event types to subscribe to (optional, defaults to all)
    - `settings`: Additional subscription settings (optional)
    
    **Hierarchical Behavior:**
    - Subscribing to "/projects" with `include_children=true` will receive notifications for "/projects/alpha", "/projects/beta", etc.
    - Path normalization is applied automatically
    """
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

@app.get(
    "/subscriptions", 
    response_model=List[SubscriptionResponse],
    tags=["subscriptions"],
    summary="Get user subscriptions",
    description="Retrieve all notification subscriptions for the current user",
    responses={
        200: {
            "description": "List of user subscriptions",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "user123",
                            "path": "/projects/alpha",
                            "include_children": True,
                            "notification_types": ["created", "updated"],
                            "settings": {"email": True}
                        }
                    ]
                }
            }
        }
    }
)
async def get_subscriptions(
    user_id: str = Depends(get_current_user_id),
    path_prefix: Optional[str] = Query(None, description="Filter subscriptions by path prefix"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all notification subscriptions for the current user.
    
    This endpoint returns all subscriptions owned by the current user,
    optionally filtered by path prefix.
    
    **Query Parameters:**
    - `path_prefix`: Optional filter to return only subscriptions for paths starting with this prefix
    
    **Example:**
    - `path_prefix="/projects"` returns subscriptions for "/projects/alpha", "/projects/beta", etc.
    """
    query = select(NotificationSubscription).filter(
        NotificationSubscription.user_id == user_id
    )
    
    if path_prefix:
        query = query.filter(NotificationSubscription.path.startswith(path_prefix))
    
    result = await db.execute(query.order_by(NotificationSubscription.path))
    return result.scalars().all()

@app.delete(
    "/subscriptions/{subscription_id}",
    tags=["subscriptions"],
    summary="Delete subscription",
    description="Delete a notification subscription",
    responses={
        200: {
            "description": "Subscription successfully deleted",
            "content": {
                "application/json": {
                    "example": {"status": "success"}
                }
            }
        },
        404: {
            "description": "Subscription not found or doesn't belong to current user"
        },
        500: {
            "description": "Internal server error during deletion"
        }
    }
)
async def delete_subscription(
    subscription_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a notification subscription.
    
    This endpoint deletes a subscription owned by the current user.
    All related notifications will have their subscription reference removed,
    but the notifications themselves are preserved.
    
    **Path Parameters:**
    - `subscription_id`: UUID of the subscription to delete
    
    **Behavior:**
    - Removes the subscription from the database
    - Updates related notifications to remove foreign key references
    - Preserves notification history for audit purposes
    """
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

@app.get(
    "/subscriptions/check", 
    response_model=SubscriptionCheckResponse,
    tags=["subscriptions"],
    summary="Check subscription status",
    description="Check if the current user is subscribed to a specific object path",
    responses={
        200: {
            "description": "Subscription check result",
            "content": {
                "application/json": {
                    "example": {
                        "path": "/projects/alpha",
                        "is_subscribed": True,
                        "direct_subscription": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "path": "/projects/alpha",
                            "include_children": True
                        },
                        "inherited_subscription": None
                    }
                }
            }
        }
    }
)
async def check_subscription(
    path: str = Query(..., description="The object path to check subscription for"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if the current user is subscribed to a specific object path.
    
    This endpoint checks for both direct subscriptions and inherited subscriptions
    from parent paths with `include_children=true`.
    
    **Query Parameters:**
    - `path`: The object path to check (e.g., "/projects/alpha")
    
    **Response:**
    - `is_subscribed`: True if user is subscribed either directly or through inheritance
    - `direct_subscription`: Details of direct subscription if exists
    - `inherited_subscription`: Details of parent subscription if notifications are inherited
    
    **Inheritance Logic:**
    - If subscribed to "/projects" with `include_children=true`, then "/projects/alpha" is also subscribed
    - The response shows both the direct subscription and the inherited subscription
    """
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
    
    # Create database schema and tables
    async with engine.begin() as conn:
        # Create the notifications schema if it doesn't exist
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS notifications"))
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
@app.get(
    "/health",
    tags=["system"],
    summary="Health check",
    description="Check the health status of the notification service",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "timestamp": "2024-01-15T10:30:00.000Z"
                    }
                }
            }
        }
    }
)
async def health():
    """
    Health check endpoint for monitoring and load balancers.
    
    This endpoint provides a simple health check for the notification service.
    It returns a 200 status code with current timestamp when the service is operational.
    
    **Response:**
    - `status`: Always "ok" when service is healthy
    - `timestamp`: Current server timestamp in ISO format
    """
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get(
    "/system/notifications", 
    response_model=List[NotificationResponse],
    tags=["system"],
    summary="Get all system notifications",
    description="Retrieve all notifications in the system for monitoring and debugging purposes",
    responses={
        200: {
            "description": "List of all notifications in the system",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "user123",
                            "type": "created",
                            "title": "New Project Alpha created",
                            "content": "John Doe created a new Project Alpha",
                            "severity": "info",
                            "timestamp": "2024-01-15T10:30:00Z",
                            "is_read": False,
                            "object_path": "/projects/alpha"
                        }
                    ]
                }
            }
        }
    }
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
    debugging, and administrative purposes. It supports the same filtering options as the
    user-specific notifications endpoint.
    
    **Administrative Endpoint:**
    - Returns notifications for all users (no user filtering)
    - Useful for system monitoring and debugging
    - Supports higher limits (up to 500) than user endpoints
    
    **Filtering:**
    - All the same filters as `/notifications` endpoint
    - Additional search includes object_path field
    """
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

@app.get(
    "/objects/hierarchy",
    tags=["system"],
    summary="Get object hierarchy",
    description="Get the hierarchical structure of all objects in the system",
    responses={
        200: {
            "description": "Hierarchical tree structure of all objects",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "path": "/projects",
                            "children": [
                                {
                                    "path": "/projects/alpha",
                                    "children": [
                                        {
                                            "path": "/projects/alpha/tasks",
                                            "children": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
)
async def get_object_hierarchy(db: AsyncSession = Depends(get_db)):
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
    
    # Get all unique object paths from notifications and subscriptions
    notification_paths_query = select(Notification.object_path).distinct()
    subscription_paths_query = select(NotificationSubscription.path).distinct()
    
    notification_result = await db.execute(notification_paths_query)
    subscription_result = await db.execute(subscription_paths_query)
    
    notification_paths = {path for (path,) in notification_result.fetchall()}
    subscription_paths = {path for (path,) in subscription_result.fetchall()}
    
    # Combine all paths
    all_paths = notification_paths.union(subscription_paths)
    
    # Build hierarchical structure
    hierarchy = {}
    
    for path in all_paths:
        # Skip empty paths
        if not path or path == '/':
            continue
            
        # Split path into segments
        segments = [seg for seg in path.split('/') if seg]
        
        # Build the hierarchy
        current_level = hierarchy
        current_path = ''
        
        for segment in segments:
            current_path += '/' + segment
            
            if segment not in current_level:
                current_level[segment] = {
                    'path': current_path,
                    'children': {}
                }
            
            current_level = current_level[segment]['children']
    
    # Convert to the format expected by the frontend
    def build_tree(node_dict):
        result = []
        for key, value in sorted(node_dict.items()):
            node = {
                'path': value['path'],
                'children': build_tree(value['children']) if value['children'] else []
            }
            result.append(node)
        return result
    
    return build_tree(hierarchy)

# Configuration endpoints
@app.get(
    "/config/severity-levels",
    tags=["configuration"],
    summary="Get severity levels configuration",
    description="Get available notification severity levels with their display configuration",
    responses={
        200: {
            "description": "Available severity levels with display configuration",
            "content": {
                "application/json": {
                    "example": {
                        "severity_levels": [
                            {
                                "value": "info",
                                "label": "Info",
                                "description": "Informational messages",
                                "bootstrap_class": "info",
                                "priority": 1
                            },
                            {
                                "value": "warning",
                                "label": "Warning",
                                "description": "Warning messages",
                                "bootstrap_class": "warning",
                                "priority": 2
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_severity_levels():
    """
    Get available notification severity levels with their display configuration.
    
    This endpoint provides the complete configuration for notification severity levels,
    including display labels, descriptions, Bootstrap CSS classes, and priority ordering.
    
    **Response Fields:**
    - `value`: Internal severity level identifier
    - `label`: Human-readable display name
    - `description`: Detailed description of the severity level
    - `bootstrap_class`: CSS class for styling (info, warning, danger, dark)
    - `priority`: Numeric priority for sorting (1 = lowest, 4 = highest)
    
    **Use Cases:**
    - Frontend dropdown filters
    - CSS styling and color coding
    - Priority-based sorting and filtering
    - Consistent UI display across components
    """
    return {
        "severity_levels": [
            {
                "value": "info",
                "label": "Info",
                "description": "Informational messages",
                "bootstrap_class": "info",
                "priority": 1
            },
            {
                "value": "warning", 
                "label": "Warning",
                "description": "Warning messages that require attention",
                "bootstrap_class": "warning",
                "priority": 2
            },
            {
                "value": "error",
                "label": "Error", 
                "description": "Error messages indicating problems",
                "bootstrap_class": "danger",
                "priority": 3
            },
            {
                "value": "critical",
                "label": "Critical",
                "description": "Critical issues requiring immediate attention",
                "bootstrap_class": "dark",
                "priority": 4
            }
        ]
    }

@app.get(
    "/config/event-types",
    tags=["configuration"],
    summary="Get event types configuration",
    description="Get available event types for filtering and subscription",
    responses={
        200: {
            "description": "Available event types with descriptions",
            "content": {
                "application/json": {
                    "example": {
                        "event_types": [
                            {
                                "value": "created",
                                "label": "Created",
                                "description": "Object creation events"
                            },
                            {
                                "value": "updated",
                                "label": "Updated",
                                "description": "Object modification events"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_event_types():
    """
    Get available event types for filtering and subscription.
    
    This endpoint provides the complete list of event types supported by the system,
    with display labels and descriptions.
    
    **Response Fields:**
    - `value`: Internal event type identifier
    - `label`: Human-readable display name
    - `description`: Detailed description of the event type
    
    **Use Cases:**
    - Frontend dropdown filters
    - Subscription configuration (selecting which events to receive)
    - Event type validation
    - Consistent UI display across components
    
    **Supported Event Types:**
    - `created`: Object creation events
    - `updated`: Object modification events
    - `deleted`: Object deletion events
    - `commented`: Comment addition events
    - `status_changed`: Status transition events
    - `assigned`: Assignment events
    """
    return {
        "event_types": [
            {
                "value": "created",
                "label": "Created",
                "description": "Object creation events"
            },
            {
                "value": "updated",
                "label": "Updated", 
                "description": "Object modification events"
            },
            {
                "value": "deleted",
                "label": "Deleted",
                "description": "Object deletion events"
            },
            {
                "value": "commented",
                "label": "Commented",
                "description": "Comment addition events"
            },
            {
                "value": "status_changed",
                "label": "Status Changed",
                "description": "Status transition events"
            },
            {
                "value": "assigned",
                "label": "Assigned",
                "description": "Assignment events"
            }
        ]
    }

@app.get(
    "/config/ui",
    tags=["configuration"],
    summary="Get UI configuration",
    description="Get UI configuration including help text and customizable content",
    responses={
        200: {
            "description": "UI configuration for frontend components",
            "content": {
                "application/json": {
                    "example": {
                        "dashboard": {
                            "title": "Notification System Demo",
                            "description": "Hierarchical notification system",
                            "features": ["Hierarchical subscriptions", "Real-time notifications"],
                            "instructions": {
                                "title": "How to use this demo:",
                                "steps": ["Subscribe to objects", "Receive notifications"]
                            }
                        },
                        "notification_center": {
                            "title": "Notification Center",
                            "default_page_size": 20,
                            "max_page_size": 100
                        }
                    }
                }
            }
        }
    }
)
async def get_ui_config():
    """
    Get UI configuration including help text and customizable content.
    
    This endpoint provides configuration for frontend UI components,
    including help text, feature descriptions, and display settings.
    
    **Configuration Sections:**
    - `dashboard`: Homepage content and instructions
    - `notification_center`: Notification display settings
    
    **Use Cases:**
    - Dynamic help text and instructions
    - Configurable UI content without code changes
    - Consistent messaging across frontend components
    - A/B testing and customization support
    
    **Backend-Driven UI:**
    - Allows updating UI content without redeploying frontend
    - Supports multiple languages and customizations
    - Centralized content management
    """
    return {
        "dashboard": {
            "title": "Notification System Demo",
            "description": "This demo showcases a hierarchical notification system with the following features:",
            "features": [
                "Subscribe to objects at any level in a hierarchy",
                "Automatically receive notifications for child objects", 
                "Real-time notification delivery via WebSockets",
                "Persistent notification history",
                "Filter and search through notifications"
            ],
            "instructions": {
                "title": "How to use this demo:",
                "steps": [
                    "Go to the Object Browser to view the hierarchical object structure",
                    "Subscribe to objects by clicking the bell icon",
                    "An event generator is randomly creating events for objects",
                    "You'll receive real-time notifications for subscribed objects and their children",
                    "View and manage your subscriptions in My Subscriptions",
                    "See all notifications in the Notification Center"
                ]
            }
        },
        "notification_center": {
            "title": "Notification Center",
            "default_page_size": 20,
            "max_page_size": 100
        }
    }

# WebSocket endpoint for real-time notifications
@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time notification streaming.
    
    This WebSocket endpoint provides real-time notification delivery to connected clients.
    When a user subscribes to this endpoint, they will receive notifications as they are created.
    
    **Path Parameters:**
    - `user_id`: The user ID to receive notifications for
    
    **Message Format:**
    - JSON-formatted notification objects
    - Same structure as REST API notification responses
    
    **Connection Management:**
    - Automatically handles connection/disconnection
    - Subscribes to user-specific NATS channel
    - Gracefully handles network issues
    
    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/notifications/user123');
    ws.onmessage = (event) => {
        const notification = JSON.parse(event.data);
        // Handle real-time notification
    };
    ```
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
            import asyncio
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
