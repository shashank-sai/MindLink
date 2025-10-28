#!/usr/bin/env python3
"""
Mock Ollama module for testing the MindLink system without actual Ollama installation.
"""

import json
import time
from typing import Dict, Any, Optional

class Client:
    """Mock Ollama client for testing."""
    
    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize mock client."""
        self.host = host
    
    def generate(self, model: str, prompt: str, options: Optional[Dict] = None, format: Optional[str] = None) -> Dict[str, Any]:
        """
        Mock generate method that simulates Ollama responses.
        
        Args:
            model: Model name
            prompt: Input prompt
            options: Generation options
            format: Response format (e.g., "json")
            
        Returns:
            Mock response dictionary
        """
        # Simulate processing time
        time.sleep(0.1)
        
        # Determine response based on model and prompt
        if "therapist" in prompt.lower() or "empathetic" in prompt.lower():
            response_text = self._generate_therapeutic_response(prompt)
        elif "medical" in prompt.lower() or "physical" in prompt.lower():
            response_text = self._generate_medical_response(prompt, format == "json")
        else:
            response_text = self._generate_general_response(prompt)
        
        return {
            "model": model,
            "response": response_text,
            "done": True,
            "context": [1, 2, 3],  # Mock context
            "total_duration": 123456789,
            "load_duration": 987654321,
            "prompt_eval_count": 42,
            "prompt_eval_duration": 12345678,
            "eval_count": 24,
            "eval_duration": 87654321
        }
    
    def _generate_therapeutic_response(self, prompt: str) -> str:
        """Generate a mock therapeutic response."""
        return "I understand you're going through a difficult time. It's important to acknowledge your feelings and take care of yourself. Would you like to talk more about what's been troubling you?"
    
    def _generate_medical_response(self, prompt: str, json_format: bool = False) -> str:
        """Generate a mock medical response."""
        if json_format:
            return json.dumps({
                "medical_concerns": ["stress-related fatigue", "sleep quality"],
                "confidence": 0.75,
                "urgency": "low",
                "recommendation": "Consider evaluating sleep patterns and stress management techniques",
                "symptoms_identified": ["fatigue", "mood changes"]
            })
        else:
            return "Based on the symptoms described, potential factors could include stress-related fatigue or sleep quality issues. Consider evaluating sleep patterns and stress management techniques."
    
    def _generate_general_response(self, prompt: str) -> str:
        """Generate a mock general response."""
        return f"I've processed your input about '{prompt[:20]}...'. This is a simulated response from the {self.host} service."

# Convenience function to match Ollama API
def generate(model: str, prompt: str, options: Optional[Dict] = None, format: Optional[str] = None) -> Dict[str, Any]:
    """
    Mock generate function.
    
    Args:
        model: Model name
        prompt: Input prompt
        options: Generation options
        format: Response format
        
    Returns:
        Mock response dictionary
    """
    client = Client()
    return client.generate(model, prompt, options, format)

# For testing
if __name__ == "__main__":
    # Test the mock client
    client = Client()
    
    # Test therapeutic response
    resp = client.generate("phi3:3.8b", "You are a professional therapist. Respond supportively to: I feel anxious")
    print("Therapeutic Response:", resp["response"])
    
    # Test medical response
    resp = client.generate("mistral:7b", "Analyze for medical conditions", format="json")
    print("Medical Response:", resp["response"])