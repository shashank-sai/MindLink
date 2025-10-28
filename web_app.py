#!/usr/bin/env python3
"""
Web interface for the MindLink tri-model therapy system.
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import TriModelOrchestrator
from core.context_engine import ContextEngine
from utils.logger import SessionLogger
from utils.safety import get_global_safety_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mindlink-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
safety_manager = get_global_safety_manager()

# Store active sessions
active_sessions = {}

class WebSession:
    """Represents a web session with its own orchestrator and context."""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.orchestrator = TriModelOrchestrator()
        self.context_engine = ContextEngine()
        self.session_logger = SessionLogger()
        self.start_time = datetime.now()
        self.is_active = True
    
    def process_message(self, user_message):
        """Process a user message through the tri-model system."""
        try:
            # Add to conversation history
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
            
            # Update the last exchange with the MindLink response
            history = self.context_engine.get_full_history()
            if history and history[-1]["mindlink"] == "":
                # Update the last exchange with the MindLink response
                self.context_engine.clear_history()
                # Re-add all previous exchanges
                for exchange in history[:-1]:
                    self.context_engine.add_exchange(exchange["user"], exchange["mindlink"])
                # Add the last exchange with the updated response
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
    
    def get_history(self):
        """Get conversation history."""
        return self.context_engine.get_full_history()
    
    def clear_history(self):
        """Clear conversation history."""
        self.context_engine.clear_history()
    
    def end_session(self):
        """End the session."""
        self.is_active = False

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connections."""
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = WebSession(session_id)
    join_room(session_id)
    emit('session_created', {'session_id': session_id})
    logger.info(f"New session created: {session_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnections."""
    # Clean up session data
    pass

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming messages from the web client."""
    session_id = data.get('session_id')
    user_message = data.get('message', '').strip()
    
    if not session_id or session_id not in active_sessions:
        emit('error', {'message': 'Invalid session'})
        return
    
    if not user_message:
        emit('error', {'message': 'Empty message'})
        return
    
    session = active_sessions[session_id]
    if not session.is_active:
        emit('error', {'message': 'Session has ended'})
        return
    
    # Emit typing indicator
    emit('typing_start')
    
    # Process message in a separate thread to avoid blocking
    def process_and_respond():
        result = session.process_message(user_message)
        
        # Emit typing end
        socketio.emit('typing_end', to=session_id)
        
        if result['success']:
            # Emit the response
            socketio.emit('message_response', {
                'response': result['response'],
                'risk_assessment': result['risk_assessment']
            }, to=session_id)
        else:
            # Emit error
            socketio.emit('error', {
                'message': result['error']
            }, to=session_id)
    
    # Start processing thread
    thread = threading.Thread(target=process_and_respond)
    thread.daemon = True
    thread.start()

@socketio.on('get_history')
def handle_get_history(data):
    """Handle requests for conversation history."""
    session_id = data.get('session_id')
    
    if not session_id or session_id not in active_sessions:
        emit('error', {'message': 'Invalid session'})
        return
    
    session = active_sessions[session_id]
    history = session.get_history()
    
    emit('history_response', {'history': history})

@socketio.on('clear_history')
def handle_clear_history(data):
    """Handle requests to clear conversation history."""
    session_id = data.get('session_id')
    
    if not session_id or session_id not in active_sessions:
        emit('error', {'message': 'Invalid session'})
        return
    
    session = active_sessions[session_id]
    session.clear_history()
    
    emit('history_cleared', {'message': 'History cleared successfully'})

@socketio.on('end_session')
def handle_end_session(data):
    """Handle requests to end the session."""
    session_id = data.get('session_id')
    
    if not session_id or session_id not in active_sessions:
        emit('error', {'message': 'Invalid session'})
        return
    
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
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()