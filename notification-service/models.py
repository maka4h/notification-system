from datetime import datetime
import json
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NotificationSubscription(Base):
    __tablename__ = "notification_subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    path = Column(String, nullable=False, index=True)
    include_children = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notification_types = Column(JSON, nullable=True)  # List of event types to subscribe to
    settings = Column(JSON, nullable=True)  # User preferences for this subscription
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "path": self.path,
            "include_children": self.include_children,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "notification_types": self.notification_types,
            "settings": self.settings
        }

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    severity = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    object_path = Column(String, nullable=False, index=True)
    action_url = Column(String, nullable=True)
    subscription_id = Column(String, ForeignKey("notification_subscriptions.id"), nullable=True)
    inherited = Column(Boolean, default=False, nullable=False)
    extra_data = Column(JSON, nullable=True)  # Renamed from metadata to avoid SQLAlchemy conflict
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_read": self.is_read,
            "object_path": self.object_path,
            "action_url": self.action_url,
            "subscription_id": self.subscription_id,
            "inherited": self.inherited,
            "extra_data": self.extra_data  # Updated to match new column name
        }
