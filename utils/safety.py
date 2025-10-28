#!/usr/bin/env python3
"""
Safety measures and disclaimers for the MindLink dual-model therapy system.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config.settings import EMERGENCY_THRESHOLD, DISCLAIMER_VISIBLE, DISCLAIMER_DURATION

class SafetyManager:
    """Manages safety protocols and disclaimers for the therapy system."""
    
    def __init__(self):
        """Initialize safety manager."""
        self.logger = logging.getLogger(__name__)
        self.disclaimer_last_shown = None
        self.emergency_contacts = [
            {"name": "National Suicide Prevention Lifeline", "number": "988"},
            {"name": "Crisis Text Line", "number": "Text HOME to 741741"},
            {"name": "Emergency Services", "number": "911"}
        ]
        
        self.logger.info("SafetyManager initialized")
    
    def get_disclaimer(self) -> str:
        """
        Get the standard medical disclaimer.
        
        Returns:
            Disclaimer text
        """
        disclaimer = (
            "=== MEDICAL DISCLAIMER ===\n"
            "MindLink is an AI therapy assistant, NOT a substitute for professional medical care.\n"
            "If you are experiencing a mental health crisis or having thoughts of self-harm,\n"
            "please contact emergency services or a crisis helpline immediately.\n"
            "\n"
            "Important contacts:\n"
        )
        
        for contact in self.emergency_contacts:
            disclaimer += f"- {contact['name']}: {contact['number']}\n"
        
        disclaimer += (
            "\nWhile this system considers potential medical correlations,\n"
            "it cannot diagnose conditions or replace medical consultation.\n"
            "Please consult with qualified healthcare professionals for medical concerns.\n"
            "=========================="
        )
        
        return disclaimer
    
    def should_show_disclaimer(self) -> bool:
        """
        Determine if disclaimer should be shown based on timing.
        
        Returns:
            True if disclaimer should be displayed
        """
        if not DISCLAIMER_VISIBLE:
            return False
            
        # Show disclaimer at start of session
        if self.disclaimer_last_shown is None:
            return True
            
        # Show disclaimer periodically
        time_since_last = datetime.now() - self.disclaimer_last_shown
        if time_since_last > timedelta(seconds=DISCLAIMER_DURATION):
            return True
            
        return False
    
    def record_disclaimer_shown(self):
        """Record that disclaimer was shown to user."""
        self.disclaimer_last_shown = datetime.now()
        self.logger.info("Disclaimer shown to user")
    
    def evaluate_emergency_risk(self, medical_analysis: Dict, user_input: str) -> Dict:
        """
        Evaluate if there's an emergency risk requiring immediate intervention.
        
        Args:
            medical_analysis: Results from medical context analysis
            user_input: User's statement
            
        Returns:
            Dictionary with risk assessment
        """
        risk_assessment = {
            "is_emergency": False,
            "risk_level": "low",
            "immediate_actions": [],
            "contact_recommendations": []
        }
        
        # Check medical analysis for high-risk indicators
        if medical_analysis.get('confidence', 0) >= EMERGENCY_THRESHOLD:
            risk_assessment["is_emergency"] = True
            risk_assessment["risk_level"] = "high"
            risk_assessment["immediate_actions"].append("Seek immediate medical attention")
            risk_assessment["contact_recommendations"].extend(self.emergency_contacts)
        
        # Check user input for crisis keywords
        crisis_keywords = [
            "suicide", "kill myself", "hurt myself", "end my life",
            "emergency", "hospital", "ambulance", "chest pain",
            "difficulty breathing", "severe headache"
        ]
        
        user_input_lower = user_input.lower()
        crisis_detected = any(keyword in user_input_lower for keyword in crisis_keywords)
        
        if crisis_detected:
            risk_assessment["is_emergency"] = True
            risk_assessment["risk_level"] = "critical"
            risk_assessment["immediate_actions"].append("Contact crisis intervention immediately")
            risk_assessment["contact_recommendations"].extend(self.emergency_contacts[:2])
        
        if risk_assessment["is_emergency"]:
            self.logger.critical(f"Emergency risk detected: {risk_assessment['risk_level']}")
        
        return risk_assessment
    
    def get_safety_intervention(self, risk_assessment: Dict) -> str:
        """
        Generate appropriate safety intervention message.
        
        Args:
            risk_assessment: Risk assessment dictionary
            
        Returns:
            Safety intervention message
        """
        if not risk_assessment.get("is_emergency", False):
            return ""
        
        risk_level = risk_assessment.get("risk_level", "low")
        actions = risk_assessment.get("immediate_actions", [])
        contacts = risk_assessment.get("contact_recommendations", [])
        
        intervention = f"\n=== URGENT SAFETY ALERT ({risk_level.upper()} RISK) ===\n"
        
        for action in actions:
            intervention += f"⚠️  {action}\n"
        
        if contacts:
            intervention += "\nIMMEDIATE CONTACT OPTIONS:\n"
            for contact in contacts:
                intervention += f"  • {contact['name']}: {contact['number']}\n"
        
        intervention += "\nThis situation requires immediate professional attention.\n"
        intervention += "===============================================\n"
        
        return intervention

# Global safety manager instance
safety_manager = SafetyManager()

def get_global_safety_manager() -> SafetyManager:
    """
    Get the global safety manager instance.
    
    Returns:
        SafetyManager instance
    """
    return safety_manager

if __name__ == "__main__":
    # Example usage
    safety_mgr = SafetyManager()
    
    # Test disclaimer
    print(safety_mgr.get_disclaimer())
    print()
    
    # Test emergency evaluation
    test_analysis = {
        "medical_concerns": ["severe dehydration"],
        "confidence": 0.95,
        "urgency": "high"
    }
    
    risk_assessment = safety_mgr.evaluate_emergency_risk(
        test_analysis, 
        "I feel dizzy and weak, like I might pass out"
    )
    
    print("Risk Assessment:", risk_assessment)
    
    # Test safety intervention
    intervention = safety_mgr.get_safety_intervention(risk_assessment)
    print("Safety Intervention:", intervention)