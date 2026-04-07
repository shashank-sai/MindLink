#!/usr/bin/env python3
"""
Web interface for the MindLink tri-model therapy system.
Now with user authentication and per-user conversation history.
"""

import os
import sys
import json
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import TriModelOrchestrator
from core.context_engine import ContextEngine
from utils.logger import SessionLogger
from utils.safety import get_global_safety_manager
from auth.auth_manager import AuthManager
from db.models import User, Conversation, Message
from config.database import get_db_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'mindlink-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
safety_manager = get_global_safety_manager()

# Store active sessions (session_id -> session_data)
active_sessions = {}


def require_auth_socket(socket_event_handler):
  """Decorator to require authentication for SocketIO events."""
  from flask import request as flask_request
  @wraps(socket_event_handler)
  def wrapped(*args, **kwargs):
    # For SocketIO, data is passed as the first argument or in kwargs
    data = args[0] if args else kwargs.get('data', {})
    if not isinstance(data, dict):
      data = {}
    
    # Try to get token from data first
    token = data.get('auth_token')
    
    if not token:
      emit('auth_required', {'message': 'Authentication required'})
      return

    auth_manager = AuthManager()
    is_valid, payload, message = auth_manager.verify_jwt_token(token)

    if not is_valid:
      emit('auth_error', {'message': message})
      return

    # Add user info to kwargs
    kwargs['user_id'] = payload.get('user_id')
    kwargs['username'] = payload.get('username')
    kwargs['auth_token'] = token

    return socket_event_handler(*args, **kwargs)
  return wrapped


class AuthenticatedSession:
    """Represents an authenticated user session with conversation history."""
    
    def __init__(self, session_id, user_id, username, auth_token):
        self.session_id = session_id
        self.user_id = user_id
        self.username = username
        self.auth_token = auth_token
        self.orchestrator = TriModelOrchestrator()
        self.context_engine = ContextEngine()
        self.session_logger = SessionLogger()
        self.start_time = datetime.now()
        self.is_active = True
        self.current_conversation = None
        self.db_session = get_db_session()
    
    def get_or_create_conversation(self, title=None):
        """Get current conversation or create a new one."""
        if self.current_conversation:
            return self.current_conversation
        
        # Create new conversation for this user
        conversation = Conversation(
            user_id=self.user_id,
            title=title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            risk_level='low'
        )
        self.db_session.add(conversation)
        self.db_session.commit()
        self.current_conversation = conversation
        return conversation
    
    def save_message(self, role, content, conversation=None):
        """Save a message to the database."""
        conv = conversation or self.get_or_create_conversation()
        
        message = Message(
            conversation_id=conv.conversation_id,
            user_id=self.user_id,
            role=role,
            content=content,
            risk_level='low'
        )
        self.db_session.add(message)
        self.db_session.commit()
        return message
    
    def get_conversation_history(self, limit=50):
        """Get user's conversation history from database."""
        try:
            conversations = self.db_session.query(Conversation).filter(
                Conversation.user_id == self.user_id,
                Conversation.is_archived == False
            ).order_by(Conversation.last_message_at.desc()).limit(limit).all()
            
            history = []
            for conv in conversations:
                messages = self.db_session.query(Message).filter(
                    Message.conversation_id == conv.conversation_id
                ).order_by(Message.timestamp.asc()).all()
                
                conv_data = {
                    'conversation_id': str(conv.conversation_id),
                    'title': conv.title,
                    'started_at': conv.started_at.isoformat() if conv.started_at else None,
                    'message_count': conv.message_count,
                    'messages': [
                        {
                            'role': msg.role,
                            'content': msg.content,
                            'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
                        }
                        for msg in messages
                    ]
                }
                history.append(conv_data)
            
            return history
        except Exception as e:
            logger.error(f"Error fetching conversation history: {e}")
            return []
    
    def process_message(self, user_message):
        """Process a user message through the tri-model system."""
        try:
            # Save user message
            self.save_message('user', user_message)
            
            # Add to context engine
            self.context_engine.add_exchange(user_message, "")
            
            # Process through the orchestrator
            therapeutic_response, medical_analysis = self.orchestrator.process_user_input(user_message)
            
            # Log interaction
            self.session_logger.log_interaction(user_message, therapeutic_response, medical_analysis)
            
            # Check for safety concerns
            risk_assessment = safety_manager.evaluate_emergency_risk(medical_analysis, user_message)
            
            # Synthesize final response
            final_response = self.orchestrator.synthesize_response(
                therapeutic_response,
                medical_analysis,
                user_message,
                self.context_engine
            )
            
            # Save bot response
            self.save_message('assistant', final_response)
            
            # Update context
            history = self.context_engine.get_full_history()
            if history and history[-1]["mindlink"] == "":
                self.context_engine.clear_history()
                for exchange in history[:-1]:
                    self.context_engine.add_exchange(exchange["user"], exchange["mindlink"])
                self.context_engine.add_exchange(history[-1]["user"], final_response)
            
            return {
                'success': True,
                'response': final_response,
                'risk_assessment': risk_assessment
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def end_session(self):
        """End the session."""
        self.is_active = True
        try:
            self.db_session.close()
        except:
            pass


@app.route('/')
def index():
    """Redirect to auth page or chat if logged in."""
    return redirect(url_for('auth_page'))


@app.route('/auth')
def auth_page():
    """Serve the authentication page."""
    return render_template('auth.html')


@app.route('/chat')
def chat_page():
    """Serve the main chat interface (requires authentication)."""
    return render_template('chat.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


# Authentication routes are in api/auth_routes.py
# Import and register them
from api.auth_routes import auth_bp
app.register_blueprint(auth_bp)


@app.route('/api/user/conversations', methods=['GET'])
def get_user_conversations():
    """Get all conversations for the authenticated user."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({'success': False, 'error': 'No token provided'}), 401
    
    auth_manager = AuthManager()
    is_valid, payload, message = auth_manager.verify_jwt_token(token)
    
    if not is_valid:
        return jsonify({'success': False, 'error': message}), 401
    
    try:
        db_session = get_db_session()
        conversations = db_session.query(Conversation).filter(
            Conversation.user_id == payload.get('user_id'),
            Conversation.is_archived == False
        ).order_by(Conversation.last_message_at.desc()).all()
        
        result = []
        for conv in conversations:
            result.append({
                'conversation_id': str(conv.conversation_id),
                'title': conv.title,
                'started_at': conv.started_at.isoformat() if conv.started_at else None,
                'message_count': conv.message_count,
                'risk_level': conv.risk_level
            })
        
        db_session.close()
        return jsonify({'success': True, 'conversations': result})
    
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversations/<conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    """Get messages for a specific conversation."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({'success': False, 'error': 'No token provided'}), 401
    
    auth_manager = AuthManager()
    is_valid, payload, message = auth_manager.verify_jwt_token(token)
    
    if not is_valid:
        return jsonify({'success': False, 'error': message}), 401
    
    try:
        db_session = get_db_session()
        conv = db_session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == payload.get('user_id')
        ).first()
        
        if not conv:
            db_session.close()
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404
        
        messages = db_session.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        result = [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in messages
        ]
        
        db_session.close()
        return jsonify({'success': True, 'messages': result})
    
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
  """Handle new WebSocket connections."""
  logger.info(f"Client connected: {request.sid}")


@socketio.on('join_session')
@require_auth_socket
def handle_join_session(data, user_id=None, username=None, auth_token=None):
  """Handle client joining a session room."""
  session_id = data.get('session_id')
  if session_id:
    from flask_socketio import join_room
    join_room(session_id)
    logger.info(f"User {username} joined session: {session_id}")
    emit('session_joined', {'session_id': session_id, 'message': 'Successfully joined session'}, to=session_id)


@socketio.on('disconnect')
def handle_disconnect():
  """Handle WebSocket disconnections."""
  # Clean up session data
  pass


@socketio.on('send_message')
@require_auth_socket
def handle_message(data, user_id=None, username=None, auth_token=None):
    """Handle incoming messages from the authenticated user."""
    session_id = data.get('session_id')
    user_message = data.get('message', '').strip()
    
    if not user_message:
        emit('error', {'message': 'Empty message'})
        return
    
    # Get or create session for this user
    if session_id not in active_sessions:
        active_sessions[session_id] = AuthenticatedSession(session_id, user_id, username, auth_token)
    
    session = active_sessions[session_id]
    
    if not session.is_active:
        emit('error', {'message': 'Session has ended'})
        return
    
    # Emit typing indicator
    emit('typing_start')
    
    # Process message in a separate thread
    def process_and_respond():
        result = session.process_message(user_message)
        
        # Emit typing end
        socketio.emit('typing_end', to=session_id)
        
        if result['success']:
            socketio.emit('message_response', {
                'response': result['response'],
                'risk_assessment': result.get('risk_assessment', {})
            }, to=session_id)
        else:
            socketio.emit('error', {
                'message': result.get('error', 'Unknown error')
            }, to=session_id)
    
    thread = threading.Thread(target=process_and_respond)
    thread.daemon = True
    thread.start()


@socketio.on('get_history')
@require_auth_socket
def handle_get_history(data, user_id=None, username=None, auth_token=None):
    """Handle requests for conversation history."""
    session_id = data.get('session_id')
    
    if session_id not in active_sessions:
        active_sessions[session_id] = AuthenticatedSession(session_id, user_id, username, auth_token)
    
    session = active_sessions[session_id]
    history = session.get_conversation_history()
    
    emit('history_response', {'history': history})


@socketio.on('clear_history')
@require_auth_socket
def handle_clear_history(data, user_id=None, username=None, auth_token=None):
    """Handle requests to clear conversation history."""
    session_id = data.get('session_id')
    
    if session_id not in active_sessions:
        active_sessions[session_id] = AuthenticatedSession(session_id, user_id, username, auth_token)
    
    session = active_sessions[session_id]
    
    # Clear context engine
    session.context_engine.clear_history()
    
    emit('history_cleared', {'message': 'History cleared successfully'})


@socketio.on('end_session')
@require_auth_socket
def handle_end_session(data, user_id=None, username=None, auth_token=None):
    """Handle requests to end the session."""
    session_id = data.get('session_id')
    
    if session_id in active_sessions:
        session = active_sessions[session_id]
        session.end_session()
        del active_sessions[session_id]
    
    leave_room(session_id)
    emit('session_ended', {'message': 'Session ended successfully'})


def main():
    """Run the web application."""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting MindLink Web Interface on port {port}")
    logger.info(f"Authentication required: True")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
