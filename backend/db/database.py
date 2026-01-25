"""
Database Connection and Session Management

This module handles:
1. Creating the database engine (connection to the database file)
2. Creating session factory (for getting database sessions)
3. Initializing the database (creating all tables)
4. Providing database sessions to the application
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
from db.conversation.models import Base  
from typing import Generator

# Create the database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=True  # TODO Remove this in production
)

# SessionLocal is a factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables.
    
    This function should be called once when the application starts.
    It checks if tables exist, and if not, creates them based on our models.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session to FastAPI endpoints.
    
    This function uses the 'yield' pattern, which ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()