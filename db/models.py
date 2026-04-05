#!/usr/bin/env python3
"""
SQLAlchemy ORM Models for MindLink database.
These models mirror the PostgreSQL schema for programmatic access.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import (
Column, String, Text, DateTime, Boolean, Integer, Numeric, ForeignKey,
Index, CheckConstraint, event
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship, declarative_base, Session
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User account model for authentication."""
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until


class UserSession(Base):
    """Active user session model."""
    __tablename__ = 'user_sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    device_info = Column(String(500))
    ip_address = Column(INET)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, active={self.is_active})>"

    def is_expired(self) -> bool:
        """Check if session has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class Conversation(Base):
    """Conversation metadata model."""
    __tablename__ = 'conversations'

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    title = Column(String(200))
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow, index=True)
    message_count = Column(Integer, default=0)
    mood_score = Column(Numeric(3, 2))
    risk_level = Column(String(20), default='low')
    vector_collection_name = Column(String(100))
    is_archived = Column(Boolean, default=False, index=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.conversation_id}, user={self.user_id})>"


class Message(Base):
    """Individual message storage model."""
    __tablename__ = 'messages'

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.conversation_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    mood_score = Column(Numeric(3, 2))
    risk_level = Column(String(20), default='low')
    vector_id = Column(String(100))  # Reference to vector DB
    message_metadata = Column(JSONB)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        CheckConstraint('role IN (\'user\', \'assistant\', \'system\')', name='chk_role'),
    )

    def __repr__(self):
        return f"<Message(role='{self.role}', timestamp={self.timestamp})>"


class UserProfile(Base):
    """Extended user profile information."""
    __tablename__ = 'user_profiles'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    preferred_name = Column(String(100))
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    notification_preferences = Column(JSONB, default={})
    therapy_goals = Column(JSONB)  # Stored as array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id})>"


class AuditLog(Base):
    """Security audit log model."""
    __tablename__ = 'audit_logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), index=True)
    action_type = Column(String(50), nullable=False, index=True)
    action_details = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(type='{self.action_type}', user={self.user_id})>"


class PasswordResetToken(Base):
    """Password reset token model."""
    __tablename__ = 'password_reset_tokens'

    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    token_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, used={self.used})>"


# Index definitions (explicit for databases that don't support partial indexes)
Index('idx_users_active', User.is_active, postgresql_where=User.is_active == True)
Index('idx_sessions_active', UserSession.is_active, postgresql_where=UserSession.is_active == True)
Index('idx_conversations_archived', Conversation.is_archived, postgresql_where=Conversation.is_archived == True)
