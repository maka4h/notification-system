"""
Legacy main.py - now imports from the clean architecture
"""
from app.main import app

# For backward compatibility, we expose the app here
__all__ = ["app"]
