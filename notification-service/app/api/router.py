"""
Main API router that includes all sub-routers
"""
from fastapi import APIRouter

from app.api import notifications, subscriptions, configuration, system, objects

api_router = APIRouter()

# Include all routers
api_router.include_router(notifications.router)
api_router.include_router(subscriptions.router)
api_router.include_router(configuration.router)
api_router.include_router(system.router)
api_router.include_router(objects.router)
