#!/usr/bin/env python3
"""
Database configuration and connection management for MindLink.
Handles PostgreSQL connections using SQLAlchemy.
"""

import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and sessions."""
    
    _instance: Optional['DatabaseManager'] = None
    _engine = None
    _session_local = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection."""
        if self._engine is not None:
            return

        # Load from .env file if not already loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        self.database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:6155@localhost:5432/MindLink'
        )
        logger.info(f"Using database URL: {self.database_url[:50]}...")
        
        try:
            self._engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            self._session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            # Fallback to in-memory SQLite for development
            logger.warning("Falling back to SQLite for development")
            self._engine = create_engine(
                'sqlite:///mindlink_dev.db',
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
            self._session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self._session_local()
    
    def check_connection(self) -> bool:
        """Check if database connection is alive."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    @property
    def session_local(self):
        """Get session factory."""
        return self._session_local


# Global database manager instance
db_manager = DatabaseManager()


def get_db_session() -> Session:
    """Get a database session for use outside of classes."""
    return db_manager.get_session()


def check_db_connection() -> bool:
    """Check database connection status."""
    return db_manager.check_connection()


def init_db():
    """Initialize database tables."""
    from db.models import Base
    db_manager._engine.connect()
    Base.metadata.create_all(bind=db_manager._engine)
    logger.info("Database tables initialized")
