#!/usr/bin/env python3
"""
Authentication API routes for MindLink.
Handles user registration, login, logout, and token management.
"""

import os
import logging
from datetime import datetime
from functools import wraps

from flask import Blueprint, request, jsonify, current_app, g
from sqlalchemy.orm import Session

from auth.auth_manager import AuthManager
from config.database import get_db_session
from db.models import User

logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def require_auth(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'success': False, 'error': 'Missing authorization header'}), 401

        # Extract token from "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({'success': False, 'error': 'Invalid authorization format'}), 401

        token = parts[1]

        # Verify token
        auth_manager = AuthManager()
        is_valid, payload, message = auth_manager.verify_jwt_token(token)

        if not is_valid:
            return jsonify({'success': False, 'error': message}), 401

        # Store user info in Flask's g object
        g.user_id = payload.get('user_id')
        g.username = payload.get('username')

        return f(*args, **kwargs)

    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Expected JSON:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "preferred_name": "string" (optional)
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        preferred_name = data.get('preferred_name', '').strip()

        # Validation
        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'Username, email, and password are required'}), 400

        if len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400

        if len(password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400

        # Register user
        auth_manager = AuthManager()
        success, message, user = auth_manager.register_user(username, email, password, preferred_name)

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user': {
                    'user_id': str(user.user_id),
                    'username': user.username,
                    'email': user.email
                }
            }), 201
        else:
            return jsonify({'success': False, 'error': message}), 400

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user.

    Expected JSON:
    {
        "username": "string",  # Can be username or email
        "password": "string"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400

        # Get device info and IP
        device_info = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.remote_addr

        # Login
        auth_manager = AuthManager()
        success, message, auth_data = auth_manager.login(username, password, device_info, ip_address)

        if success:
            response = jsonify({
                'success': True,
                'message': message,
                'data': auth_data
            })

            # Set token in cookie (optional)
            response.set_cookie('auth_token', auth_data['token'], max_age=86400)  # 24 hours

            return response, 200
        else:
            return jsonify({'success': False, 'error': message}), 401

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout current user."""
    try:
        auth_manager = AuthManager()
        success = auth_manager.logout(g.user_id)

        if success:
            response = jsonify({'success': True, 'message': 'Logged out successfully'})
            response.delete_cookie('auth_token')
            return response, 200
        else:
            return jsonify({'success': False, 'error': 'Logout failed'}), 500

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information."""
    try:
        auth_manager = AuthManager()
        user = auth_manager.get_user_by_id(g.user_id)

        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        return jsonify({
            'success': True,
            'user': {
                'user_id': str(user.user_id),
                'username': user.username,
                'email': user.email,
                'preferred_name': user.profile.preferred_name if user.profile else None,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/me', methods=['PUT'])
@require_auth
def update_current_user():
    """Update current user profile."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        auth_manager = AuthManager()
        db_session = auth_manager.db_session

        user = db_session.query(User).filter(User.user_id == g.user_id).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Update profile
        if 'preferred_name' in data:
            if user.profile:
                user.profile.preferred_name = data['preferred_name']

        if 'timezone' in data:
            if user.profile:
                user.profile.timezone = data['timezone']

        db_session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200

    except Exception as e:
        logger.error(f"Update user error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()

        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400

        auth_manager = AuthManager()
        success, message, reset_token = auth_manager.request_password_reset(email)

        # Always return success to prevent email enumeration
        return jsonify({
            'success': True,
            'message': 'If the email exists, a password reset link has been sent'
        }), 200

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token."""
    try:
        data = request.get_json()
        token = data.get('token', '')
        new_password = data.get('password', '')

        if not token or not new_password:
            return jsonify({'success': False, 'error': 'Token and new password are required'}), 400

        if len(new_password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400

        auth_manager = AuthManager()
        success, message = auth_manager.reset_password(token, new_password)

        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'error': message}), 400

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """Refresh JWT token."""
    try:
        auth_manager = AuthManager()

        # Generate new token
        from db.models import User
        user = auth_manager.get_user_by_id(g.user_id)

        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        token_data = auth_manager.generate_jwt_token(user.user_id, user.username, user.email)

        return jsonify({
            'success': True,
            'token': token_data['token'],
            'expires_at': token_data['exp']
        }), 200

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
