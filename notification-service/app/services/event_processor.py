"""
NATS event processing service
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any

import nats
from sqlalchemy.ext.asyncio import AsyncSession

from models import Notification
from app.services import NotificationService, SubscriptionService
from app.core.config import get_async_session

logger = logging.getLogger(__name__)


class EventProcessor:
    """Processes events from NATS and creates notifications"""
    
    def __init__(self, nc: nats.NATS):
        self.nc = nc
    
    async def process_event(self, msg):
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
            
            async with get_async_session() as db:
                subscription_service = SubscriptionService(db)
                notification_service = NotificationService(db)
                
                # Get all parent paths
                parent_paths = self._get_parent_paths(normalized_path)
                
                # Find subscribers for this path
                subscribed_users = await self._get_subscribed_users(
                    db, normalized_path, parent_paths, event_type
                )
                
                # Process notifications for each subscriber
                for user_id, subscription in subscribed_users.items():
                    try:
                        notification = await notification_service.create_notification(
                            user_id=user_id,
                            event_type=event_type,
                            object_path=normalized_path,
                            payload=payload,
                            subscription_id=subscription.id,
                            inherited=subscription.path != normalized_path
                        )
                        
                        # Also publish to user's notification channel for real-time updates
                        notification_data = notification.to_dict()
                        await self.nc.publish(
                            f"notification.user.{user_id}",
                            json.dumps(notification_data).encode()
                        )
                    except Exception as e:
                        logger.error(f"Error creating notification for user {user_id}: {e}")
                
                # Create a system-level notification for debugging/monitoring purposes
                try:
                    system_notification = await notification_service.create_notification(
                        user_id="system",  # Special system user for monitoring
                        event_type=event_type,
                        object_path=normalized_path,
                        payload={**payload, "system_event": True}
                    )
                except Exception as e:
                    logger.error(f"Error creating system notification: {e}")
                    
        except Exception as e:
            logger.exception(f"Error processing event: {e}")
    
    async def _get_subscribed_users(
        self, 
        db: AsyncSession, 
        path: str, 
        parent_paths: list, 
        event_type: str
    ) -> Dict[str, Any]:
        """Get all users subscribed to a path"""
        from app.repositories import SubscriptionRepository
        
        subscription_repo = SubscriptionRepository(db)
        
        # Find direct and parent subscriptions
        subscriptions = await subscription_repo.get_subscriptions_for_path(path, parent_paths)
        
        # Filter and deduplicate subscribers
        subscribed_users = {}  # user_id -> subscription
        
        for subscription in subscriptions:
            # Check if this event type is in allowed types
            if (subscription.notification_types and 
                event_type not in subscription.notification_types):
                continue
            
            # Use direct subscription over inherited if both exist
            if subscription.user_id not in subscribed_users:
                subscribed_users[subscription.user_id] = subscription
            elif subscription.path == path:  # Direct subscription takes precedence
                subscribed_users[subscription.user_id] = subscription
        
        return subscribed_users
    
    def _get_parent_paths(self, path: str) -> list:
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
