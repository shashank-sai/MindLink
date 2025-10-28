#!/usr/bin/env python3
"""
Logging utilities for the MindLink dual-model therapy system.
"""

import logging
import os
from datetime import datetime
from config.settings import LOG_LEVEL, LOG_FILE

def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Suppress verbose logging from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('ollama').setLevel(logging.WARNING)
    
    logging.info("Logging system initialized")

def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger instance.
    
    Args:
        name: Name for the logger
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

class SessionLogger:
    """Tracks session-specific information and metrics."""
    
    def __init__(self, session_id: str = ""):
        """Initialize session logger."""
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = get_logger(f"session.{self.session_id}")
        self.interactions = 0
        self.medical_flags = 0
        
        self.logger.info(f"Session started: {self.session_id}")
    
    def log_interaction(self, user_input: str, therapeutic_response: str, 
                       medical_analysis: dict = {}):
        """
        Log a complete interaction cycle.
        
        Args:
            user_input: User's statement
            therapeutic_response: Therapist's response
            medical_analysis: Medical analysis results (optional)
        """
        self.interactions += 1
        
        # Log basic interaction
        self.logger.info(f"Interaction {self.interactions}: User input length={len(user_input)}")
        
        # Log medical analysis if present
        if medical_analysis and medical_analysis.get('medical_concerns'):
            self.medical_flags += 1
            concerns = ', '.join(medical_analysis.get('medical_concerns', []))
            self.logger.info(f"Medical concerns detected: {concerns} "
                           f"(confidence: {medical_analysis.get('confidence', 0):.2f})")
    
    def get_session_summary(self) -> dict:
        """
        Get session summary statistics.
        
        Returns:
            Dictionary with session metrics
        """
        return {
            "session_id": self.session_id,
            "total_interactions": self.interactions,
            "medical_flags_raised": self.medical_flags,
            "medical_flag_rate": self.medical_flags / max(self.interactions, 1)
        }

if __name__ == "__main__":
    # Example usage
    setup_logging()
    
    # Create session logger
    session = SessionLogger()
    
    # Log some interactions
    session.log_interaction(
        "I feel anxious all the time",
        "I understand you're experiencing persistent anxiety...",
        {"medical_concerns": ["thyroid issues"], "confidence": 0.8}
    )
    
    session.log_interaction(
        "Thanks for listening",
        "You're welcome. I'm here to support you."
    )
    
    # Print session summary
    summary = session.get_session_summary()
    print("Session Summary:", summary)