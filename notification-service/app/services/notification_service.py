"""
Service layer for business logic
"""
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from models import Notification, NotificationSubscription, SeverityLevel, EventType
from schemas import SubscriptionCheckResponse, SubscriptionResponse
from app.repositories import (
    NotificationRepository,
    SubscriptionRepository,
    SeverityLevelRepository,
    EventTypeRepository,
)
from schemas import SubscriptionCreate, SubscriptionCheckResponse, BulkMarkAsReadRequest, BulkMarkAsReadResponse


class ConfigurationService:
    """Service for configuration-related operations"""
    
    def __init__(self, session: AsyncSession):
        self.severity_repo = SeverityLevelRepository(session)
        self.event_type_repo = EventTypeRepository(session)
    
    async def get_severity_levels(self) -> Dict[str, List[Dict]]:
        """Get all active severity levels"""
        severity_levels = await self.severity_repo.get_all_active()
        return {
            "severity_levels": [level.to_dict() for level in severity_levels]
        }
    
    async def get_event_types(self) -> Dict[str, List[Dict]]:
        """Get all active event types"""
        event_types = await self.event_type_repo.get_all_active()
        return {
            "event_types": [event_type.to_dict() for event_type in event_types]
        }
    
    async def get_severity_for_event_type(self, event_type: str) -> str:
        """Get the default severity for an event type"""
        event_type_obj = await self.event_type_repo.get_by_id(event_type)
        if event_type_obj and event_type_obj.default_severity_id:
            return event_type_obj.default_severity_id
        return "info"  # Default fallback
    
    @staticmethod
    def get_ui_config() -> Dict[str, Any]:
        """Get UI configuration"""
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


class NotificationService:
    """Service for notification-related operations"""
    
    def __init__(self, session: AsyncSession):
        self.notification_repo = NotificationRepository(session)
        self.subscription_repo = SubscriptionRepository(session)
        self.config_service = ConfigurationService(session)
    
    async def get_notifications(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        **filters
    ) -> List[Notification]:
        """Get notifications for a user with filtering"""
        return await self.notification_repo.get_by_user_id(
            user_id, limit, offset, **filters
        )
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        return await self.notification_repo.mark_as_read(notification_id, user_id)
    
    async def bulk_mark_as_read(
        self, 
        request: BulkMarkAsReadRequest, 
        user_id: str
    ) -> BulkMarkAsReadResponse:
        """Mark multiple notifications as read"""
        if not request.notification_ids:
            raise ValueError("No notification IDs provided")
        
        updated_count = await self.notification_repo.bulk_mark_as_read(
            request.notification_ids, user_id
        )
        
        return BulkMarkAsReadResponse(
            status="success",
            updated_count=updated_count,
            message=f"{updated_count} notifications marked as read"
        )
    
    async def create_notification(
        self,
        user_id: str,
        event_type: str,
        object_path: str,
        payload: Dict[str, Any],
        subscription_id: Optional[str] = None,
        inherited: bool = False
    ) -> Notification:
        """Create a new notification"""
        # Get severity from event type
        severity = await self.config_service.get_severity_for_event_type(event_type)
        
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=event_type,
            title=self._generate_title(object_path, event_type),
            content=self._generate_content(object_path, event_type, payload),
            severity=severity,
            timestamp=datetime.utcnow(),
            is_read=False,
            object_path=object_path,
            action_url=self._generate_action_url(object_path),
            subscription_id=subscription_id,
            inherited=inherited,
            extra_data={
                "object_path": object_path,
                "subscription_path": subscription_id,
                "payload": payload
            }
        )
        
        return await self.notification_repo.create(notification)
    
    def _generate_title(self, path: str, event_type: str) -> str:
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
    
    def _generate_content(self, path: str, event_type: str, payload: Dict[str, Any]) -> str:
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
    
    def _generate_action_url(self, path: str) -> str:
        """Generate a URL for the notification action"""
        # In a real app, this would map to your frontend routes
        return f"/app{path}"


class SubscriptionService:
    """Service for subscription-related operations"""
    
    def __init__(self, session: AsyncSession):
        self.subscription_repo = SubscriptionRepository(session)
    
    async def create_subscription(
        self, 
        subscription_data: SubscriptionCreate, 
        user_id: str
    ) -> NotificationSubscription:
        """Create a new subscription or update existing one"""
        # Normalize the path
        path = subscription_data.path if subscription_data.path.startswith('/') else '/' + subscription_data.path
        
        # Check if subscription already exists
        existing = await self.subscription_repo.get_by_user_and_path(user_id, path)
        
        if existing:
            # Update existing
            existing.include_children = subscription_data.include_children
            existing.notification_types = subscription_data.notification_types
            existing.settings = subscription_data.settings
            return await self.subscription_repo.update(existing)
        
        # Create new
        new_subscription = NotificationSubscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            path=path,
            include_children=subscription_data.include_children,
            notification_types=subscription_data.notification_types,
            settings=subscription_data.settings,
        )
        
        return await self.subscription_repo.create(new_subscription)
    
    async def get_subscriptions(
        self, 
        user_id: str, 
        path_prefix: Optional[str] = None
    ) -> List[NotificationSubscription]:
        """Get all subscriptions for a user"""
        return await self.subscription_repo.get_by_user_id(user_id, path_prefix)
    
    async def delete_subscription(self, subscription_id: str, user_id: str) -> bool:
        """Delete a subscription"""
        subscription = await self.subscription_repo.get_by_id(subscription_id, user_id)
        if not subscription:
            return False
        
        await self.subscription_repo.delete(subscription)
        return True
    
    async def check_subscription(
        self, 
        path: str, 
        user_id: str
    ) -> SubscriptionCheckResponse:
        """Check if user is subscribed to a path"""
        # Normalize path
        normalized_path = path if path.startswith('/') else '/' + path
        
        # Get all parent paths
        parent_paths = self._get_parent_paths(normalized_path)
        
        # Check direct subscription
        direct_sub = await self.subscription_repo.get_by_user_and_path(user_id, normalized_path)
        
        # Check inherited subscription (from parent with include_children=True)
        parent_sub = None
        if parent_paths:
            from sqlalchemy import select, func
            from sqlalchemy.ext.asyncio import AsyncSession
            # This is a simplified approach - in practice you'd want to optimize this
            for parent_path in parent_paths:
                potential_parent = await self.subscription_repo.get_by_user_and_path(user_id, parent_path)
                if potential_parent and potential_parent.include_children:
                    parent_sub = potential_parent
                    break
        
        return SubscriptionCheckResponse(
            path=normalized_path,
            is_subscribed=direct_sub is not None or parent_sub is not None,
            direct_subscription=SubscriptionResponse.model_validate(direct_sub) if direct_sub else None,
            inherited_subscription=SubscriptionResponse.model_validate(parent_sub) if parent_sub else None
        )
    
    def _get_parent_paths(self, path: str) -> List[str]:
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


class SystemService:
    """Service for system-related operations"""
    
    def __init__(self, session: AsyncSession):
        self.notification_repo = NotificationRepository(session)
        self.subscription_repo = SubscriptionRepository(session)
    
    async def get_all_notifications(
        self,
        limit: int = 100,
        offset: int = 0,
        **filters
    ) -> List[Notification]:
        """Get all notifications in the system for monitoring"""
        from sqlalchemy import select, or_
        
        query = (
            select(Notification)
            .order_by(Notification.timestamp.desc())
        )
        
        # Apply filters
        if filters.get('path'):
            query = query.filter(Notification.object_path == filters['path'])
        if filters.get('event_type'):
            query = query.filter(Notification.type == filters['event_type'])
        if filters.get('severity'):
            query = query.filter(Notification.severity == filters['severity'])
        if filters.get('from_date'):
            query = query.filter(Notification.timestamp >= filters['from_date'])
        if filters.get('to_date'):
            query = query.filter(Notification.timestamp <= filters['to_date'])
        if filters.get('is_read') is not None:
            query = query.filter(Notification.is_read == filters['is_read'])
        if filters.get('search'):
            search_pattern = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Notification.title.ilike(search_pattern),
                    Notification.content.ilike(search_pattern),
                    Notification.object_path.ilike(search_pattern)
                )
            )
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        session = self.notification_repo.session
        result = await session.execute(query)
        return result.scalars().all()
    
    async def get_object_hierarchy(self) -> List[Dict[str, Any]]:
        """Get the hierarchical structure of all objects"""
        from sqlalchemy import select
        
        # Get all unique object paths from notifications and subscriptions
        session = self.notification_repo.session
        
        notification_paths_query = select(Notification.object_path).distinct()
        subscription_paths_query = select(NotificationSubscription.path).distinct()
        
        notification_result = await session.execute(notification_paths_query)
        subscription_result = await session.execute(subscription_paths_query)
        
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
