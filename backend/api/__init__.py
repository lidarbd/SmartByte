"""
API Module

This module aggregates all API routers for the SmartByte application.

The module provides:
- Conversation API: Customer-facing chat and recommendations
- Admin API: Administrative functions, metrics, and data management

Usage in main.py:
    from backend.api import conversation_router, admin_router
    
    app.include_router(conversation_router, prefix="/api/conversation")
    app.include_router(admin_router, prefix="/api")
"""

from .conversation import router as conversation_router
from .admin import router as admin_router

__all__ = ['conversation_router', 'admin_router']