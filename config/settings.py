#!/usr/bin/env python3
"""
Configuration settings for the MindLink dual-model therapy system.
"""

# Model configurations
THERAPIST_MODEL = "phi3:3.8b"  # Therapeutic Specialist (SLM)
SENTINEL_MODEL = "mistral:7b"   # Medical Context Sentinel (GLM)
SYNTHESIS_MODEL = "phi3.5:3.8b"   # Response Synthesis and Follow-up Generator (larger model)

# Ollama configuration
OLLAMA_HOST = "http://localhost:11434"

# Safety thresholds
MEDICAL_CONCERN_THRESHOLD = 0.7  # Confidence threshold for medical concerns
EMERGENCY_THRESHOLD = 0.9       # Threshold for immediate medical referral

# UI settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FONT_FAMILY = "Arial"
FONT_SIZE = 12

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "mindlink.log"

# Disclaimer settings
DISCLAIMER_VISIBLE = True
DISCLAIMER_DURATION = 10  # seconds