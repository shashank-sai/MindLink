#!/usr/bin/env python3
"""
Context Engine for the MindLink dual-model therapy system.
Manages session-specific context and conversation history.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from collections import deque

class ContextEngine:
    """Manages session-specific context and conversation history."""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the context engine.
        
        Args:
            max_history: Maximum number of conversation exchanges to retain
        """
        self.logger = logging.getLogger(__name__)
        self.max_history = max_history
        self.conversation_history = deque(maxlen=max_history)
        self.session_start_time = datetime.now()
        self.context_data = {}
        
        self.logger.info(f"ContextEngine initialized with max_history={max_history}")
    
    def add_exchange(self, user_input: str, mindlink_response: str):
        """
        Add a conversation exchange to the history.
        
        Args:
            user_input: User's message
            mindlink_response: System's response
        """
        exchange = {
            "user": user_input,
            "mindlink": mindlink_response,
            "timestamp": datetime.now()
        }
        self.conversation_history.append(exchange)
        self.logger.debug(f"Added exchange to history. Current history length: {len(self.conversation_history)}")
    
    def get_recent_history(self, count: int = 3) -> List[Dict]:
        """
        Get recent conversation history.
        
        Args:
            count: Number of recent exchanges to retrieve
            
        Returns:
            List of recent conversation exchanges
        """
        return list(self.conversation_history)[-count:]
    
    def get_full_history(self) -> List[Dict]:
        """
        Get the full conversation history.
        
        Returns:
            List of all conversation exchanges
        """
        return list(self.conversation_history)
    
    def set_context(self, key: str, value: Any):
        """
        Set a context variable.
        
        Args:
            key: Context variable name
            value: Context variable value
        """
        self.context_data[key] = value
        self.logger.debug(f"Set context variable '{key}' to '{value}'")
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a context variable.
        
        Args:
            key: Context variable name
            default: Default value if key not found
            
        Returns:
            Context variable value or default
        """
        return self.context_data.get(key, default)
    
    def get_session_duration(self) -> float:
        """
        Get the session duration in seconds.
        
        Returns:
            Session duration in seconds
        """
        return (datetime.now() - self.session_start_time).total_seconds()
    
    def get_session_info(self) -> Dict:
        """
        Get session information.
        
        Returns:
            Dictionary with session information
        """
        duration = self.get_session_duration()
        return {
            "session_start_time": self.session_start_time.isoformat(),
            "session_duration_seconds": duration,
            "interaction_count": len(self.conversation_history),
            "context_variables": self.context_data.copy()
        }
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")
    
    def reset_context(self):
        """Reset all context variables."""
        self.context_data.clear()
        self.logger.info("Context variables reset")

if __name__ == "__main__":
    # Example usage
    context_engine = ContextEngine()
    
    # Add some conversation exchanges
    context_engine.add_exchange("Hello, how are you?", "I'm doing well, thank you for asking!")
    context_engine.add_exchange("I've been feeling stressed lately.", "I'm sorry to hear that. Would you like to talk about what's been causing your stress?")
    
    # Set some context variables
    context_engine.set_context("user_mood", "anxious")
    context_engine.set_context("discussed_topics", ["stress", "work"])
    
    # Get recent history
    recent = context_engine.get_recent_history(2)
    print("Recent History:", recent)
    
    # Get context variable
    mood = context_engine.get_context("user_mood")
    print("User Mood:", mood)
    
    # Get session info
    session_info = context_engine.get_session_info()
    print("Session Info:", session_info)