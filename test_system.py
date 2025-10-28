#!/usr/bin/env python3
"""
Simple test script to verify the MindLink system works without Ollama installed.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from core.orchestrator import DualModelOrchestrator
        print("✓ Orchestrator imported successfully")
    except Exception as e:
        print(f"✗ Failed to import orchestrator: {e}")
        return False
    
    try:
        from core.therapist import TherapeuticSpecialist
        print("✓ Therapist imported successfully")
    except Exception as e:
        print(f"✗ Failed to import therapist: {e}")
        return False
    
    try:
        from core.sentinel import MedicalContextSentinel
        print("✓ Sentinel imported successfully")
    except Exception as e:
        print(f"✗ Failed to import sentinel: {e}")
        return False
    
    try:
        from utils.logger import setup_logging, SessionLogger
        print("✓ Logger imported successfully")
    except Exception as e:
        print(f"✗ Failed to import logger: {e}")
        return False
    
    try:
        from utils.safety import SafetyManager
        print("✓ Safety manager imported successfully")
    except Exception as e:
        print(f"✗ Failed to import safety manager: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic system functionality with mock models."""
    print("\nTesting basic functionality...")
    
    try:
        from core.orchestrator import DualModelOrchestrator
        
        # Create orchestrator instance
        orchestrator = DualModelOrchestrator()
        print("✓ Orchestrator instantiated successfully")
        
        # Test processing a simple input
        test_input = "I've been feeling tired and depressed lately."
        therapeutic_response, medical_analysis = orchestrator.process_user_input(test_input)
        
        print(f"✓ Input processed successfully")
        print(f"  Therapeutic response: {therapeutic_response[:50]}...")
        print(f"  Medical analysis: {medical_analysis}")
        
        # Test response synthesis
        final_response = orchestrator.synthesize_response(therapeutic_response, medical_analysis)
        print(f"✓ Response synthesized: {final_response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed basic functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("MindLink System Test")
    print("=" * 30)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return 1
    
    # Test functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed!")
        return 1
    
    print("\n✅ All tests passed!")
    print("\nSystem is ready for use. Run 'python main.py' to start the application.")
    return 0

if __name__ == "__main__":
    sys.exit(main())