"""
Base class for all SQLAlchemy models.

This module contains only the declarative base that all models inherit from.
Keeping it separate allows us to import it without circular dependencies.
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()