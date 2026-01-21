"""
Models Package

This package exports all database models for easy importing.
Instead of importing from individual files, you can import from this package.

"""

from .base import Base
from .product import Product
from .conversation import ChatSession, ChatMessage, Recommendation

# Export all models for easy importing
__all__ = [
    'Base',
    'Product',
    'ChatSession',
    'ChatMessage',
    'Recommendation'
]