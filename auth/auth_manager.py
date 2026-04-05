#!/usr/bin/env python3
"""
Authentication module for MindLink.
Handles user registration, login, password management, and JWT tokens.
"""

import os
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from uuid import UUID

import bcrypt
import jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.models import User, UserSession, UserProfile, AuditLog, PasswordResetToken
from config.database import get_db_session

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'dev_secret_change_in_production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# Security settings
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


class AuthManager:
    """
    Manages user authentication including registration, login,
    password management, and JWT token operations.
    """

    def __init__(self, db_session: Optional[Session] = None):
        """Initialize auth manager with database session."""
        self.db_session = db_session or get_db_session()
        self.logger = logger

    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Hash a password with bcrypt.
    
        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)
    
        Returns:
            Tuple of (password_hash, salt_str)
        """
        if salt is None:
            salt = bcrypt.gensalt(rounds=12)
        elif isinstance(salt, str):
            salt = salt.encode('utf-8')
    
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        # Store salt as string (not hex) since bcrypt salt is already a string
        return password_hash.decode('utf-8'), salt.decode('utf-8')

    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """
        Verify a password against stored hash.
        Note: bcrypt stores the salt within the hash itself, so we just need
        to compare the provided password against the stored hash.
    
        Args:
            password: Plain text password to verify
            password_hash: Stored password hash (includes salt)
            salt: Stored salt (not used for bcrypt verification)
    
        Returns:
            True if password matches, False otherwise
        """
        try:
            # bcrypt.checkpw extracts the salt from the hash automatically
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False

    def register_user(self, username: str, email: str, password: str,
                      preferred_name: Optional[str] = None) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user.

        Args:
            username: Desired username
            email: User's email address
            password: Plain text password
            preferred_name: Optional display name

        Returns:
            Tuple of (success, message, user_object)
        """
        try:
            # Check if username or email already exists
            existing_user = self.db_session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing_user:
                if existing_user.username == username:
                    return False, "Username already taken", None
                if existing_user.email == email:
                    return False, "Email already registered", None

            # Create password hash
            password_hash, salt = self._hash_password(password)

            # Create new user
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                salt=salt,
                is_verified=False
            )

            self.db_session.add(new_user)
            self.db_session.flush()  # Get the user_id

            # Create user profile
            profile = UserProfile(
                user_id=new_user.user_id,
                preferred_name=preferred_name or username
            )
            self.db_session.add(profile)

            # Audit log
            self._log_action(new_user.user_id, "USER_REGISTERED", {"email": email})

            self.db_session.commit()
            self.logger.info(f"New user registered: {username} ({email})")

            return True, "Registration successful", new_user

        except IntegrityError as e:
            self.db_session.rollback()
            self.logger.error(f"Database integrity error during registration: {e}")
            return False, "Database error during registration", None
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}", None

    def login(self, username: str, password: str,
              device_info: Optional[str] = None,
              ip_address: Optional[str] = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate a user.

        Args:
            username: Username or email
            password: Plain text password
            device_info: Optional device information
            ip_address: Optional IP address

        Returns:
            Tuple of (success, message, auth_data)
            auth_data contains: user_id, token, expires_at
        """
        try:
            # Find user by username or email
            user = self.db_session.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()

            if not user:
                self.logger.warning(f"Login attempt for non-existent user: {username}")
                return False, "Invalid credentials", None

            # Check if account is locked
            if user.is_locked():
                self._log_action(user.user_id, "LOGIN_ATTEMPT_LOCKED", {"ip": ip_address})
                return False, f"Account locked until {user.locked_until}", None

            # Verify password
            if not self._verify_password(password, user.password_hash, user.salt):
                # Increment failed attempts
                user.failed_login_attempts += 1

                if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                    self._log_action(user.user_id, "ACCOUNT_LOCKED", {"attempts": user.failed_login_attempts})
                    return False, f"Account locked for {LOCKOUT_DURATION_MINUTES} minutes", None

                self.db_session.commit()
                self._log_action(user.user_id, "LOGIN_FAILED", {"ip": ip_address})
                return False, "Invalid credentials", None

            # Check if user is active
            if not user.is_active:
                return False, "Account is deactivated", None

            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            user.locked_until = None
            
            # Generate JWT token
            token = self.generate_jwt_token(user.user_id, user.username, user.email)
            
            # Create session
            session = self.create_session(
                user.user_id,
                device_info=device_info,
                ip_address=ip_address
            )
            
            self.db_session.commit()
            self._log_action(user.user_id, "LOGIN_SUCCESS", {"ip": ip_address})
            
            # Calculate expiration time
            exp = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
            
            auth_data = {
                "user_id": str(user.user_id),
                "username": user.username,
                "email": user.email,
                "token": token,
                "session_id": str(session.session_id),
                "expires_at": exp
            }
            
            return True, "Login successful", auth_data

        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Login error: {e}")
            return False, f"Login failed: {str(e)}", None

    def logout(self, user_id: UUID) -> bool:
        """
        Log out a user by deactivating their session.

        Args:
            user_id: User's UUID

        Returns:
            True if successful
        """
        try:
            sessions = self.db_session.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).all()

            for session in sessions:
                session.is_active = False

            self.db_session.commit()
            self._log_action(user_id, "LOGOUT")
            return True

        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Logout error: {e}")
            return False

    def generate_jwt_token(self, user_id: UUID, username: str, email: str) -> str:
        """
        Generate a JWT token for a user.
    
        Args:
            user_id: User's UUID
            username: Username
            email: User's email
    
        Returns:
            Encoded JWT token string
        """
        now = datetime.utcnow()
        exp = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    
        payload = {
            "user_id": str(user_id),
            "username": username,
            "email": email,
            "exp": exp,
            "iat": now,
            "type": "access"
        }
    
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def verify_jwt_token(self, token: str) -> Tuple[bool, Optional[dict], str]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Tuple of (is_valid, payload, message)
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                return False, None, "Token expired"

            return True, payload, "Token valid"

        except jwt.ExpiredSignatureError:
            return False, None, "Token expired"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid token: {e}"

    def create_session(self, user_id: UUID, device_info: Optional[str] = None,
                       ip_address: Optional[str] = None) -> UserSession:
        """
        Create a new user session.

        Args:
            user_id: User's UUID
            device_info: Optional device information
            ip_address: Optional IP address

        Returns:
            Created UserSession object
        """
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at
        )

        self.db_session.add(session)
        return session

    def request_password_reset(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Request a password reset token.

        Args:
            email: User's email

        Returns:
            Tuple of (success, message, reset_token)
        """
        try:
            user = self.db_session.query(User).filter(User.email == email).first()

            if not user:
                # Don't reveal if email exists
                return True, "If the email exists, a reset link has been sent", None

            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(reset_token.encode()).hexdigest()

            # Store token
            reset = PasswordResetToken(
                user_id=user.user_id,
                token_hash=token_hash,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )

            self.db_session.add(reset)
            self.db_session.commit()

            self._log_action(user.user_id, "PASSWORD_RESET_REQUESTED")

            return True, "Reset token generated", reset_token

        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Password reset error: {e}")
            return False, "Failed to process reset request", None

    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password using a reset token.

        Args:
            token: Reset token
            new_password: New plain text password

        Returns:
            Tuple of (success, message)
        """
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            reset = self.db_session.query(PasswordResetToken).filter(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            ).first()

            if not reset:
                return False, "Invalid or expired token"

            # Update password
            user = self.db_session.query(User).filter(User.user_id == reset.user_id).first()
            password_hash, salt = self._hash_password(new_password)

            user.password_hash = password_hash
            user.salt = salt
            user.failed_login_attempts = 0
            user.locked_until = None

            # Mark token as used
            reset.used = True

            self.db_session.commit()
            self._log_action(user.user_id, "PASSWORD_RESET_COMPLETED")

            return True, "Password reset successful"

        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Password reset error: {e}")
            return False, "Failed to reset password"

    def _log_action(self, user_id: UUID, action_type: str, details: Optional[dict] = None):
        """Log an audit action."""
        try:
            audit = AuditLog(
                user_id=user_id,
                action_type=action_type,
                action_details=details
            )
            self.db_session.add(audit)
            self.db_session.flush()  # Don't commit here, let caller commit
        except Exception as e:
            self.logger.error(f"Failed to log audit action: {e}")

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return self.db_session.query(User).filter(User.user_id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db_session.query(User).filter(User.username == username).first()

    def __del__(self):
        """Cleanup database session."""
        try:
            self.db_session.close()
        except:
            pass
