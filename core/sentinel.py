#!/usr/bin/env python3
"""
Medical Context Sentinel module for the MindLink dual-model therapy system.
Handles interactions with the general language model for medical context analysis.
"""

import logging
import json
from typing import Dict, List, Optional
import ollama

from config.settings import SENTINEL_MODEL, OLLAMA_HOST, MEDICAL_CONCERN_THRESHOLD

class MedicalContextSentinel:
    """Interface to the Medical Context Sentinel (GLM) model."""
    
    def __init__(self):
        """Initialize the medical context sentinel model."""
        self.logger = logging.getLogger(__name__)
        self.model_name = SENTINEL_MODEL
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.concern_threshold = MEDICAL_CONCERN_THRESHOLD
        
        self.logger.info(f"MedicalContextSentinel initialized with model: {self.model_name}")
    
    def analyze_medical_context(self, user_input: str) -> Dict:
        """
        Analyze user input for potential medical correlations.
        
        Args:
            user_input: The user's statement to analyze
            
        Returns:
            Dictionary containing medical analysis results
        """
        try:
            # Structured prompt for medical analysis
            medical_prompt = f"""Analyze the following statement for potential medical conditions that could contribute to these symptoms. 
Focus on physical health issues that might manifest as psychological symptoms.

Statement: "{user_input}"

Respond ONLY in valid JSON format with this exact structure:
{{
    "medical_concerns": ["condition1", "condition2"],
    "confidence": 0.0 to 1.0,
    "urgency": "low|medium|high",
    "recommendation": "brief recommendation if medical consultation needed",
    "symptoms_identified": ["symptom1", "symptom2"]
}}

If no significant medical correlations are found, return:
{{
    "medical_concerns": [],
    "confidence": 0.0,
    "urgency": "low",
    "recommendation": "Continue with therapeutic support",
    "symptoms_identified": []
}}

Examples of physical conditions that can cause psychological symptoms:
- Thyroid disorders (anxiety, depression)
- Vitamin deficiencies (B12, D) (fatigue, mood changes)
- Sleep disorders (irritability, cognitive issues)
- Hormonal imbalances (mood swings)
- Chronic pain conditions (depression)
- Neurological conditions (cognitive changes)

Provide your analysis:"""
            
            # Generate structured response
            response = self.client.generate(
                model=self.model_name,
                prompt=medical_prompt,
                format="json",
                options={
                    "temperature": 0.3,    # Focused analysis
                    "top_p": 0.8,
                    "repeat_penalty": 1.3  # Avoid repetition
                }
            )
            
            # Try to parse the JSON response
            try:
                analysis = json.loads(response['response'])
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                self.logger.warning("Failed to parse JSON response, using fallback structure")
                analysis = {
                    "medical_concerns": [],
                    "confidence": 0.0,
                    "urgency": "low",
                    "recommendation": "Continue with therapeutic support",
                    "symptoms_identified": []
                }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in medical context analysis: {e}")
            # Return safe fallback
            return {
                "medical_concerns": [],
                "confidence": 0.0,
                "urgency": "low",
                "recommendation": "Continue with therapeutic support",
                "symptoms_identified": []
            }
    
    def requires_medical_attention(self, analysis: Dict) -> bool:
        """
        Determine if the analysis indicates need for medical attention.
        
        Args:
            analysis: Medical analysis dictionary
            
        Returns:
            True if medical attention is recommended
        """
        confidence = analysis.get('confidence', 0)
        urgency = analysis.get('urgency', 'low')
        
        # High confidence or high urgency triggers medical attention flag
        if confidence >= self.concern_threshold or urgency == 'high':
            return True
        return False
    
    def get_medical_summary(self, analysis: Dict) -> str:
        """
        Generate a human-readable summary of medical analysis.
        
        Args:
            analysis: Medical analysis dictionary
            
        Returns:
            Summary string for inclusion in therapeutic response
        """
        if not analysis.get('medical_concerns'):
            return ""
        
        concerns = ", ".join(analysis.get('medical_concerns', []))
        confidence = analysis.get('confidence', 0)
        recommendation = analysis.get('recommendation', '')
        
        return (f"Note: Physical factors such as {concerns} (confidence: {confidence:.1%}) "
               f"may be contributing to your experience. {recommendation}")

if __name__ == "__main__":
    # Example usage
    sentinel = MedicalContextSentinel()
    
    # Test input with potential medical correlation
    test_input = "I've been feeling really tired and depressed lately, even though I'm getting enough sleep."
    
    # Analyze medical context
    analysis = sentinel.analyze_medical_context(test_input)
    print("Medical Analysis:", json.dumps(analysis, indent=2))
    
    # Check if medical attention is needed
    needs_attention = sentinel.requires_medical_attention(analysis)
    print("Requires Medical Attention:", needs_attention)
    
    # Get summary
    summary = sentinel.get_medical_summary(analysis)
    print("Medical Summary:", summary)