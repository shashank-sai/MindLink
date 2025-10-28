#!/usr/bin/env python3
"""
Test suite for the MindLink dual-model therapy system.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestMindLinkSystem(unittest.TestCase):
    """Test cases for the MindLink system components."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def test_system_imports(self):
        """Test that all modules can be imported without errors."""
        try:
            from main import main
            from config.settings import THERAPIST_MODEL, SENTINEL_MODEL
            from core.orchestrator import DualModelOrchestrator
            from core.therapist import TherapeuticSpecialist
            from core.sentinel import MedicalContextSentinel
            from utils.logger import setup_logging, SessionLogger
            from utils.safety import SafetyManager
            from ui.desktop_app import TherapyApp
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_settings_configuration(self):
        """Test that settings are properly configured."""
        from config.settings import THERAPIST_MODEL, SENTINEL_MODEL, OLLAMA_HOST
        
        # Check that models are defined
        self.assertIsNotNone(THERAPIST_MODEL)
        self.assertIsNotNone(SENTINEL_MODEL)
        self.assertIn("http", OLLAMA_HOST)
    
    @patch('core.orchestrator.ollama.Client')
    def test_orchestrator_initialization(self, mock_client):
        """Test orchestrator initialization."""
        from core.orchestrator import DualModelOrchestrator
        
        # Mock the Ollama client
        mock_client.return_value = MagicMock()
        
        # Create orchestrator instance
        orchestrator = DualModelOrchestrator()
        
        # Verify initialization
        self.assertIsNotNone(orchestrator)
        self.assertIsNotNone(orchestrator.client)
    
    @patch('core.therapist.ollama.Client')
    def test_therapist_initialization(self, mock_client):
        """Test therapeutic specialist initialization."""
        from core.therapist import TherapeuticSpecialist
        
        # Mock the Ollama client
        mock_client.return_value = MagicMock()
        
        # Create therapist instance
        therapist = TherapeuticSpecialist()
        
        # Verify initialization
        self.assertIsNotNone(therapist)
        self.assertIsNotNone(therapist.client)
    
    @patch('core.sentinel.ollama.Client')
    def test_sentinel_initialization(self, mock_client):
        """Test medical context sentinel initialization."""
        from core.sentinel import MedicalContextSentinel
        
        # Mock the Ollama client
        mock_client.return_value = MagicMock()
        
        # Create sentinel instance
        sentinel = MedicalContextSentinel()
        
        # Verify initialization
        self.assertIsNotNone(sentinel)
        self.assertIsNotNone(sentinel.client)
    
    def test_safety_manager(self):
        """Test safety manager functionality."""
        from utils.safety import SafetyManager
        
        # Create safety manager
        safety_mgr = SafetyManager()
        
        # Test disclaimer generation
        disclaimer = safety_mgr.get_disclaimer()
        self.assertIsInstance(disclaimer, str)
        self.assertGreater(len(disclaimer), 0)
        
        # Test emergency evaluation
        test_analysis = {
            "medical_concerns": ["hypothyroidism"],
            "confidence": 0.85,
            "urgency": "medium"
        }
        
        risk_assessment = safety_mgr.evaluate_emergency_risk(
            test_analysis, 
            "I feel tired and depressed"
        )
        
        self.assertIsInstance(risk_assessment, dict)
    
    def test_logger_setup(self):
        """Test logger initialization."""
        from utils.logger import setup_logging, SessionLogger
        
        # Test setup doesn't raise exception
        try:
            setup_logging()
        except Exception as e:
            self.fail(f"Logger setup failed: {e}")
        
        # Test session logger
        session = SessionLogger()
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.session_id)

def run_all_tests():
    """Run all test cases."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMindLinkSystem)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running MindLink System Tests...")
    print("=" * 40)
    
    success = run_all_tests()
    
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)