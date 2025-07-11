"""
API routes for subscriptions
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import SubscriptionCreate, SubscriptionResponse, SubscriptionCheckResponse
from app.services import SubscriptionService
from app.core.dependencies import get_db, get_current_user_id

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post(
    "", 
    response_model=SubscriptionResponse,
    summary="Create notification subscription",
    description="Create a new notification subscription for a hierarchical object path",
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
    """
    service = SubscriptionService(db)
    return await service.create_subscription(subscription, user_id)


@router.get(
    "", 
    response_model=List[SubscriptionResponse],
    summary="Get user subscriptions",
    description="Retrieve all notification subscriptions for the current user",
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
    """
    service = SubscriptionService(db)
    return await service.get_subscriptions(user_id, path_prefix)


@router.delete(
    "/{subscription_id}",
    summary="Delete subscription",
    description="Delete a notification subscription",
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
    """
    service = SubscriptionService(db)
    success = await service.delete_subscription(subscription_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"status": "success"}


@router.get(
    "/check", 
    response_model=SubscriptionCheckResponse,
    summary="Check subscription status",
    description="Check if the current user is subscribed to a specific object path",
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
    """
    service = SubscriptionService(db)
    return await service.check_subscription(path, user_id)
