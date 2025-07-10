from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Subscription schemas
class SubscriptionCreate(BaseModel):
    path: str
    include_children: bool = True
    notification_types: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    path: str
    include_children: bool
    created_at: datetime
    notification_types: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True

# Notification schemas
class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    content: str
    severity: str
    timestamp: datetime
    is_read: bool
    object_path: str
    action_url: Optional[str] = None
    subscription_id: Optional[str] = None
    inherited: bool = False
    extra_data: Optional[Dict[str, Any]] = None  # Renamed from metadata
    
    class Config:
        orm_mode = True

# Subscription check response
class SubscriptionCheckResponse(BaseModel):
    path: str
    is_subscribed: bool
    direct_subscription: Optional[SubscriptionResponse] = None
    inherited_subscription: Optional[SubscriptionResponse] = None

# Bulk operations schemas
class BulkMarkAsReadRequest(BaseModel):
    notification_ids: List[str] = Field(..., description="List of notification IDs to mark as read")

class BulkMarkAsReadResponse(BaseModel):
    status: str
    updated_count: int
    message: str
