#!/usr/bin/env python3
"""
Orchestration layer for the MindLink dual-model therapy system.
Coordinates the Therapeutic Specialist and Medical Context Sentinel.
"""

import threading
import queue
import time
import logging
from typing import Dict, Tuple, Optional
import ollama
import json

from config.settings import THERAPIST_MODEL, SENTINEL_MODEL, OLLAMA_HOST

class DualModelOrchestrator:
    """Coordinates the dual-model system for therapy sessions."""
    
    def __init__(self):
        """Initialize the orchestrator with both models."""
        self.logger = logging.getLogger(__name__)
        self.therapist_model = THERAPIST_MODEL
        self.sentinel_model = SENTINEL_MODEL
        
        # Initialize Ollama client
        self.client = ollama.Client(host=OLLAMA_HOST)
        
        # Response queues for concurrent processing
        self.therapist_queue = queue.Queue()
        self.sentinel_queue = queue.Queue()
        
        self.logger.info("DualModelOrchestrator initialized")
    
    def _generate_therapist_response(self, prompt: str) -> str:
        """Generate therapeutic response from the SLM."""
        try:
            response = self.client.generate(
                model=self.therapist_model,
                prompt=f"You are a professional therapist. Provide an empathetic, supportive response to: {prompt}",
                options={
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            )
            return response['response']
        except Exception as e:
            self.logger.error(f"Error generating therapist response: {e}")
            return "I'm here to listen and support you."
    
    def _generate_medical_analysis(self, prompt: str) -> Dict:
        """Generate medical context analysis from the GLM."""
        try:
            # Prompt designed to elicit medical correlation analysis
            medical_prompt = f"""Analyze the following statement for potential medical conditions that could contribute to these symptoms. 
            Focus on physical health issues that might manifest as psychological symptoms.
            
            Statement: {prompt}
            
            Respond in JSON format with:
            1. medical_concerns: list of potential medical issues
            2. confidence: confidence score (0-1)
            3. urgency: urgency level (low/medium/high)
            4. recommendation: brief recommendation if medical consultation needed
            
            Example format:
            {{
                "medical_concerns": ["thyroid dysfunction", "vitamin D deficiency"],
                "confidence": 0.8,
                "urgency": "medium",
                "recommendation": "Consider blood tests for thyroid function and vitamin levels"
            }}
            """
            
            response = self.client.generate(
                model=self.sentinel_model,
                prompt=medical_prompt,
                format="json",
                options={
                    "temperature": 0.3,
                    "top_p": 0.8
                }
            )
            
            # Parse JSON response
            try:
                parsed_response = json.loads(response['response'])
                return parsed_response
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON response: {e}")
                # Return safe fallback
                return {
                    "medical_concerns": [],
                    "confidence": 0.0,
                    "urgency": "low",
                    "recommendation": "Continue with therapeutic support",
                    "symptoms_identified": []
                }
        except Exception as e:
            self.logger.error(f"Error generating medical analysis: {e}")
            return {
                "medical_concerns": [],
                "confidence": 0.0,
                "urgency": "low",
                "recommendation": "Continue with therapeutic support"
            }
    
    def process_user_input(self, user_input: str) -> Tuple[str, Dict]:
        """
        Process user input through both models concurrently.
        
        Args:
            user_input: The user's statement
            
        Returns:
            Tuple of (therapeutic_response, medical_analysis)
        """
        self.logger.info(f"Processing user input: {user_input[:50]}...")
        
        # Create threads for concurrent processing
        therapist_thread = threading.Thread(
            target=lambda q, arg1: q.put(self._generate_therapist_response(arg1)),
            args=(self.therapist_queue, user_input)
        )
        
        sentinel_thread = threading.Thread(
            target=lambda q, arg1: q.put(self._generate_medical_analysis(arg1)),
            args=(self.sentinel_queue, user_input)
        )
        
        # Start both threads
        therapist_thread.start()
        sentinel_thread.start()
        
        # Wait for both to complete
        therapist_thread.join()
        sentinel_thread.join()
        
        # Retrieve results
        therapeutic_response = self.therapist_queue.get()
        medical_analysis = self.sentinel_queue.get()
        
        self.logger.info("Both models processed successfully")
        
        return therapeutic_response, medical_analysis
    
    def synthesize_response(self, therapeutic_response: str, medical_analysis: Dict) -> str:
        """
        Synthesize the therapeutic response with medical context awareness.
        
        Args:
            therapeutic_response: Response from the therapeutic specialist
            medical_analysis: Analysis from the medical context sentinel
            
        Returns:
            Final synthesized response
        """
        # Check for high-confidence medical concerns
        if medical_analysis.get('confidence', 0) >= 0.7:
            concerns = ', '.join(medical_analysis.get('medical_concerns', []))
            recommendation = medical_analysis.get('recommendation', '')
            
            # Prepend medical context to therapeutic response
            return (f"[MEDICAL CONTEXT AWARENESS: Potential physical factors ({concerns}) "
                   f"may be contributing to your experience. {recommendation}] "
                   f"\n\n{therapeutic_response}")
        
        # Return standard therapeutic response
        return therapeutic_response

if __name__ == "__main__":
    # Example usage
    orchestrator = DualModelOrchestrator()
    
    # Test input
    test_input = "I've been feeling really tired and depressed lately, even though I'm getting enough sleep."
    
    # Process through both models
    therapeutic_resp, medical_analysis = orchestrator.process_user_input(test_input)
    
    # Synthesize final response
    final_response = orchestrator.synthesize_response(therapeutic_resp, medical_analysis)
    
    print("Therapeutic Response:", therapeutic_resp)
    print("\nMedical Analysis:", medical_analysis)
    print("\nFinal Synthesized Response:", final_response)