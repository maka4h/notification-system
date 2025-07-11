"""
Repository layer for database access
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import SeverityLevel, EventType, Notification, NotificationSubscription


class SeverityLevelRepository:
    """Repository for severity level operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_active(self) -> List[SeverityLevel]:
        """Get all active severity levels ordered by priority"""
        result = await self.session.execute(
            select(SeverityLevel)
            .filter(SeverityLevel.is_active == True)
            .order_by(SeverityLevel.priority)
        )
        return result.scalars().all()
    
    async def get_by_id(self, severity_id: str) -> Optional[SeverityLevel]:
        """Get severity level by ID"""
        result = await self.session.execute(
            select(SeverityLevel).filter(SeverityLevel.id == severity_id)
        )
        return result.scalar_one_or_none()


class EventTypeRepository:
    """Repository for event type operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_active(self) -> List[EventType]:
        """Get all active event types"""
        result = await self.session.execute(
            select(EventType)
            .filter(EventType.is_active == True)
            .order_by(EventType.label)
        )
        return result.scalars().all()
    
    async def get_by_id(self, event_type_id: str) -> Optional[EventType]:
        """Get event type by ID"""
        result = await self.session.execute(
            select(EventType).filter(EventType.id == event_type_id)
        )
        return result.scalar_one_or_none()


class NotificationRepository:
    """Repository for notification operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        self.session.add(notification)
        await self.session.commit()
        return notification
    
    async def get_by_user_id(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0,
        **filters
    ) -> List[Notification]:
        """Get notifications for a user with optional filters"""
        query = (
            select(Notification)
            .filter(Notification.user_id == user_id)
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
            from sqlalchemy import or_
            search_pattern = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Notification.title.ilike(search_pattern),
                    Notification.content.ilike(search_pattern),
                )
            )
        
        result = await self.session.execute(query.offset(offset).limit(limit))
        return result.scalars().all()
    
    async def get_by_id(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """Get notification by ID for a specific user"""
        result = await self.session.execute(
            select(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        notification = await self.get_by_id(notification_id, user_id)
        if notification:
            notification.is_read = True
            await self.session.commit()
            return True
        return False
    
    async def bulk_mark_as_read(self, notification_ids: List[str], user_id: str) -> int:
        """Mark multiple notifications as read"""
        from sqlalchemy import update, and_
        result = await self.session.execute(
            update(Notification)
            .where(
                and_(
                    Notification.id.in_(notification_ids),
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .values(is_read=True)
        )
        await self.session.commit()
        return result.rowcount


class SubscriptionRepository:
    """Repository for subscription operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, subscription: NotificationSubscription) -> NotificationSubscription:
        """Create a new subscription"""
        self.session.add(subscription)
        await self.session.commit()
        return subscription
    
    async def get_by_user_and_path(self, user_id: str, path: str) -> Optional[NotificationSubscription]:
        """Get subscription by user and path"""
        result = await self.session.execute(
            select(NotificationSubscription).filter(
                NotificationSubscription.user_id == user_id,
                NotificationSubscription.path == path
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str, path_prefix: Optional[str] = None) -> List[NotificationSubscription]:
        """Get all subscriptions for a user"""
        query = select(NotificationSubscription).filter(
            NotificationSubscription.user_id == user_id
        )
        
        if path_prefix:
            query = query.filter(NotificationSubscription.path.startswith(path_prefix))
        
        result = await self.session.execute(query.order_by(NotificationSubscription.path))
        return result.scalars().all()
    
    async def get_by_id(self, subscription_id: str, user_id: str) -> Optional[NotificationSubscription]:
        """Get subscription by ID for a specific user"""
        result = await self.session.execute(
            select(NotificationSubscription).filter(
                NotificationSubscription.id == subscription_id,
                NotificationSubscription.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def delete(self, subscription: NotificationSubscription) -> None:
        """Delete a subscription"""
        # Update related notifications to remove foreign key reference
        from sqlalchemy import update
        await self.session.execute(
            update(Notification)
            .where(Notification.subscription_id == subscription.id)
            .values(subscription_id=None)
        )
        await self.session.flush()
        
        # Delete the subscription
        await self.session.delete(subscription)
        await self.session.commit()
    
    async def update(self, subscription: NotificationSubscription) -> NotificationSubscription:
        """Update a subscription"""
        await self.session.commit()
        return subscription
    
    async def get_subscriptions_for_path(self, path: str, parent_paths: List[str]) -> List[NotificationSubscription]:
        """Get subscriptions that would be notified for a given path"""
        # Direct subscriptions
        direct_query = select(NotificationSubscription).filter(
            NotificationSubscription.path == path
        )
        direct_result = await self.session.execute(direct_query)
        direct_subs = direct_result.scalars().all()
        
        # Parent subscriptions with include_children=True
        parent_subs = []
        if parent_paths:
            parent_query = select(NotificationSubscription).filter(
                NotificationSubscription.path.in_(parent_paths),
                NotificationSubscription.include_children == True
            )
            parent_result = await self.session.execute(parent_query)
            parent_subs = parent_result.scalars().all()
        
        return direct_subs + parent_subs
