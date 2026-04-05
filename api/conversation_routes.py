#!/usr/bin/env python3
"""
Conversation API routes for MindLink.
Handles conversation management and message sending with vector DB integration.
"""

import os
import logging
from datetime import datetime
from uuid import uuid4
from functools import wraps

from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session

from db.models import Conversation, Message, User
from db.database import get_db_session
from auth.auth_manager import AuthManager
from core.vector_context_engine import VectorAwareContextEngine
from core.orchestrator import TriModelOrchestrator
from vector_store.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

# Create blueprint
conversation_bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'success': False, 'error': 'Missing authorization header'}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({'success': False, 'error': 'Invalid authorization format'}), 401

        token = parts[1]
        auth_manager = AuthManager()
        is_valid, payload, message = auth_manager.verify_jwt_token(token)

        if not is_valid:
            return jsonify({'success': False, 'error': message}), 401

        g.user_id = payload.get('user_id')
        g.username = payload.get('username')

        return f(*args, **kwargs)

    return decorated


@conversation_bp.route('', methods=['GET'])
@require_auth
def list_conversations():
    """List all conversations for the current user."""
    try:
        db_session = get_db_session()
        user_id = g.user_id

        conversations = db_session.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_archived == False
        ).order_by(Conversation.last_message_at.desc()).all()

        result = []
        for conv in conversations:
            result.append({
                'conversation_id': str(conv.conversation_id),
                'title': conv.title or 'New Conversation',
                'started_at': conv.started_at.isoformat() if conv.started_at else None,
                'last_message_at': conv.last_message_at.isoformat() if conv.last_message_at else None,
                'message_count': conv.message_count,
                'risk_level': conv.risk_level
            })

        return jsonify({
            'success': True,
            'conversations': result
        }), 200

    except Exception as e:
        logger.error(f"List conversations error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@conversation_bp.route('', methods=['POST'])
@require_auth
def create_conversation():
    """Create a new conversation."""
    try:
        data = request.get_json() or {}
        db_session = get_db_session()
        user_id = g.user_id

        # Create new conversation
        new_conv = Conversation(
            user_id=user_id,
            title=data.get('title', 'New Conversation'),
            vector_collection_name=f"user_{user_id}_conversations"
        )

        db_session.add(new_conv)
        db_session.commit()

        return jsonify({
            'success': True,
            'conversation': {
                'conversation_id': str(new_conv.conversation_id),
                'title': new_conv.title,
                'started_at': new_conv.started_at.isoformat() if new_conv.started_at else None
            }
        }), 201

    except Exception as e:
        logger.error(f"Create conversation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@conversation_bp.route('/<conversation_id>', methods=['GET'])
@require_auth
def get_conversation(conversation_id):
    """Get a specific conversation with messages."""
    try:
        db_session = get_db_session()
        user_id = g.user_id

        conv = db_session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conv:
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404

        messages = db_session.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()

        message_list = []
        for msg in messages:
            message_list.append({
                'message_id': str(msg.message_id),
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None,
                'mood_score': float(msg.mood_score) if msg.mood_score else None
            })

        return jsonify({
            'success': True,
            'conversation': {
                'conversation_id': str(conv.conversation_id),
                'title': conv.title,
                'message_count': conv.message_count
            },
            'messages': message_list
        }), 200

    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@conversation_bp.route('/<conversation_id>/messages', methods=['POST'])
@require_auth
def send_message(conversation_id):
    """
    Send a message in a conversation.
    This is the main endpoint for conversation interaction.
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        db_session = get_db_session()
        user_id = g.user_id

        # Verify conversation exists
        conv = db_session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conv:
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404

        # Store user message
        user_msg = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role='user',
            content=user_message
        )
        db_session.add(user_msg)
        db_session.flush()

        # Get context from vector DB
        context_engine = VectorAwareContextEngine(
            user_id=str(user_id),
            conversation_id=conversation_id
        )

        # Get contextual response (includes relevant history from vector DB)
        context = context_engine.get_contextual_response(user_message)

        # Use orchestrator to generate response
        orchestrator = TriModelOrchestrator()
        therapeutic_response, medical_analysis = orchestrator.process_user_input(user_message)

        # Build enhanced prompt with context
        final_response = orchestrator.synthesize_response(
            therapeutic_response,
            medical_analysis,
            user_message,
            context_engine=context_engine
        )

        # Store assistant response
        assistant_msg = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role='assistant',
            content=final_response
        )
        db_session.add(assistant_msg)
        db_session.commit()

        return jsonify({
            'success': True,
            'response': final_response,
            'context': {
                'has_long_term_memory': context.get('has_long_term_memory', False),
                'recent_count': len(context.get('recent', [])),
                'relevant_count': len(context.get('relevant', []))
            }
        }), 200

    except Exception as e:
        logger.error(f"Send message error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@conversation_bp.route('/<conversation_id>', methods=['DELETE'])
@require_auth
def delete_conversation(conversation_id):
    """Delete a conversation."""
    try:
        db_session = get_db_session()
        user_id = g.user_id

        conv = db_session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conv:
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404

        # Delete from database
        db_session.delete(conv)
        db_session.commit()

        return jsonify({
            'success': True,
            'message': 'Conversation deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Delete conversation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@conversation_bp.route('/<conversation_id>/export', methods=['GET'])
@require_auth
def export_conversation(conversation_id):
    """Export conversation data."""
    try:
        db_session = get_db_session()
        user_id = g.user_id

        conv = db_session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conv:
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404

        messages = db_session.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()

        export_data = {
            'conversation_id': str(conv.conversation_id),
            'title': conv.title,
            'started_at': conv.started_at.isoformat() if conv.started_at else None,
            'exported_at': datetime.utcnow().isoformat(),
            'messages': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
                }
                for msg in messages
            ]
        }

        return jsonify({
            'success': True,
            'data': export_data
        }), 200

    except Exception as e:
        logger.error(f"Export conversation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
