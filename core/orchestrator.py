#!/usr/bin/env python3
"""
Orchestration layer for the MindLink tri-model therapy system.
Coordinates the Therapeutic Specialist, Medical Context Sentinel, and Response Synthesis models.
"""

import threading
import queue
import time
import logging
from typing import Dict, Tuple, Optional
import ollama
import json

from config.settings import THERAPIST_MODEL, SENTINEL_MODEL, SYNTHESIS_MODEL, OLLAMA_HOST

class TriModelOrchestrator:
    """Coordinates the tri-model system for therapy sessions."""
    
    def __init__(self):
        """Initialize the orchestrator with all three models."""
        self.logger = logging.getLogger(__name__)
        self.therapist_model = THERAPIST_MODEL
        self.sentinel_model = SENTINEL_MODEL
        self.synthesis_model = SYNTHESIS_MODEL
        
        # Initialize Ollama client
        self.client = ollama.Client(host=OLLAMA_HOST)
        
        # Response queues for concurrent processing
        self.therapist_queue = queue.Queue()
        self.sentinel_queue = queue.Queue()
        self.synthesis_queue = queue.Queue()
        
        self.logger.info("TriModelOrchestrator initialized")
    
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
    
    def _generate_synthesis_response(self, therapeutic_response: str, medical_analysis: Dict, user_input: str, conversation_history: list) -> str:
        """Generate final response using the larger synthesis model."""
        try:
            # Build conversation history context
            history_text = ""
            if conversation_history:
                history_text = "\n".join([f"User: {exchange['user']}\nAssistant: {exchange['mindlink']}"
                                        for exchange in conversation_history[-3:]])  # Last 3 exchanges
            
            # Create synthesis prompt
            synthesis_prompt = f"""You are an expert at combining therapeutic wisdom with medical context awareness to provide helpful, focused responses.
            
Previous conversation:
{history_text}

Latest user input: {user_input}

Therapeutic perspective: {therapeutic_response}

Medical analysis: {json.dumps(medical_analysis, indent=2)}

Your task:
1. Combine these perspectives into a coherent, helpful response
2. If there are clear medical concerns, ask targeted follow-up questions to narrow down the root cause
3. If the user has provided sufficient information, summarize the key factors and provide practical recommendations
4. Maintain a supportive, empathetic tone while being precise and focused
5. Avoid repetitive questions - build on what's already been discussed
6. When the user indicates they've shared all relevant information, provide a comprehensive summary

Respond directly with the final response:"""
            
            response = self.client.generate(
                model=self.synthesis_model,
                prompt=synthesis_prompt,
                options={
                    "temperature": 0.5,  # More focused responses
                    "top_p": 0.8
                }
            )
            
            return response['response'].strip()
        except Exception as e:
            self.logger.error(f"Error generating synthesis response: {e}")
            return therapeutic_response
    
    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        Process user input through both models concurrently.
        
        Args:
            user_input: The user's statement
            context: Additional context information
            
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
    
    def synthesize_response(self, therapeutic_response: str, medical_analysis: Dict, user_input: str, context_engine=None) -> str:
        """
        Synthesize the final response using the third model.
        
        Args:
            therapeutic_response: Response from the therapeutic specialist
            medical_analysis: Analysis from the medical context sentinel
            user_input: Original user input
            context_engine: Context engine for session history
            
        Returns:
            Final synthesized response
        """
        # Get conversation history if available
        conversation_history = []
        if context_engine:
            conversation_history = context_engine.get_full_history()
        
        # Generate final response using the synthesis model
        final_response = self._generate_synthesis_response(
            therapeutic_response, 
            medical_analysis, 
            user_input, 
            conversation_history
        )
        
        return final_response

if __name__ == "__main__":
    # Example usage
    orchestrator = TriModelOrchestrator()
    
    # Test input
    test_input = "I've been feeling really tired and depressed lately, even though I'm getting enough sleep."
    
    # Process through both models
    therapeutic_resp, medical_analysis = orchestrator.process_user_input(test_input)
    
    # Synthesize final response
    final_response = orchestrator.synthesize_response(therapeutic_resp, medical_analysis, test_input)
    
    print("Therapeutic Response:", therapeutic_resp)
    print("\nMedical Analysis:", medical_analysis)
    print("\nFinal Synthesized Response:", final_response)