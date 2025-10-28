#!/usr/bin/env python3
"""
Therapeutic Specialist module for the MindLink dual-model therapy system.
Handles interactions with the small language model specialized in therapy.
"""

import logging
from typing import Optional
import ollama

from config.settings import THERAPIST_MODEL, OLLAMA_HOST

class TherapeuticSpecialist:
    """Interface to the Therapeutic Specialist (SLM) model."""
    
    def __init__(self):
        """Initialize the therapeutic specialist model."""
        self.logger = logging.getLogger(__name__)
        self.model_name = THERAPIST_MODEL
        self.client = ollama.Client(host=OLLAMA_HOST)
        
        self.logger.info(f"TherapeuticSpecialist initialized with model: {self.model_name}")
    
    def generate_response(self, user_input: str, conversation_history: Optional[list] = None) -> str:
        """
        Generate a therapeutic response to user input.
        
        Args:
            user_input: The user's current statement
            conversation_history: Previous conversation exchanges (optional)
            
        Returns:
            Therapeutic response from the SLM
        """
        try:
            # Build context-aware prompt
            if conversation_history:
                history_text = "\n".join([f"User: {exchange['user']}\nTherapist: {exchange['therapist']}" 
                                        for exchange in conversation_history[-3:]])  # Last 3 exchanges
                prompt = (f"Previous conversation:\n{history_text}\n\n"
                         f"User: {user_input}\n"
                         f"Provide an empathetic, supportive therapeutic response:")
            else:
                prompt = f"You are a professional therapist. Respond supportively to: {user_input}"
            
            # Generate response with therapeutic parameters
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.7,    # Balanced creativity
                    "top_p": 0.9,          # Diversity in responses
                    "repeat_penalty": 1.2  # Reduce repetition
                }
            )
            
            return response['response'].strip()
            
        except Exception as e:
            self.logger.error(f"Error generating therapeutic response: {e}")
            return "I'm here to listen and support you through this."
    
    def generate_cb_ttechnique(self, user_concern: str) -> str:
        """
        Generate a Cognitive Behavioral Therapy technique suggestion.
        
        Args:
            user_concern: The user's primary concern
            
        Returns:
            CBT technique recommendation
        """
        try:
            cbt_prompt = (f"The user is experiencing: {user_concern}. "
                         f"Suggest an appropriate CBT technique they could try, "
                         f"explaining how it works and why it might help.")
            
            response = self.client.generate(
                model=self.model_name,
                prompt=cbt_prompt,
                options={
                    "temperature": 0.5,  # More focused responses
                    "top_p": 0.8
                }
            )
            
            return response['response'].strip()
            
        except Exception as e:
            self.logger.error(f"Error generating CBT technique: {e}")
            return "A helpful CBT technique would be to practice mindfulness and observe your thoughts without judgment."
    
    def validate_approach(self, proposed_response: str) -> bool:
        """
        Validate that a therapeutic response follows ethical guidelines.
        
        Args:
            proposed_response: Response to validate
            
        Returns:
            True if response passes validation
        """
        # Basic validation checks
        prohibited_terms = [
            'diagnose', 'prescribe', 'medication', 
            'cure', 'guarantee', 'emergency'
        ]
        
        response_lower = proposed_response.lower()
        
        # Check for prohibited terms
        for term in prohibited_terms:
            if term in response_lower:
                self.logger.warning(f"Validation failed: Prohibited term '{term}' found in response")
                return False
        
        # Check for medical advice indicators
        medical_indicators = ['you should see a doctor', 'medical attention', 'hospital']
        for indicator in medical_indicators:
            if indicator in response_lower:
                self.logger.info(f"Response contains medical referral: {indicator}")
                # Not necessarily invalid, but flagged for review
        
        return True

if __name__ == "__main__":
    # Example usage
    therapist = TherapeuticSpecialist()
    
    # Test inputs
    test_input = "I've been feeling overwhelmed with work stress lately."
    
    # Generate response
    response = therapist.generate_response(test_input)
    print("Therapeutic Response:", response)
    
    # Validate response
    is_valid = therapist.validate_approach(response)
    print("Response Valid:", is_valid)
    
    # Generate CBT technique
    cbt_technique = therapist.generate_cb_ttechnique("work stress")
    print("CBT Technique:", cbt_technique)