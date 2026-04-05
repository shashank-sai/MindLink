#!/usr/bin/env python3
"""
Configuration settings for the MindLink dual-model therapy system.
"""
import os

# ===========================================
# Model configurations
# ===========================================
THERAPIST_MODEL = os.getenv('THERAPIST_MODEL', 'phi3:3.8b')
SENTINEL_MODEL = os.getenv('SENTINEL_MODEL', 'mistral:7b')
SYNTHESIS_MODEL = os.getenv('SYNTHESIS_MODEL', 'phi3.5:3.8b')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')

# Ollama configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

# ===========================================
# Database configuration
# ===========================================
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://mindlink_user:password@localhost:5432/mindlink')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_NAME = os.getenv('DB_NAME', 'mindlink')
DB_USER = os.getenv('DB_USER', 'mindlink_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

# ===========================================
# Vector Database (ChromaDB)
# ===========================================
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', './chroma_db')
CHROMA_DB_HOST = os.getenv('CHROMA_DB_HOST', None)
CHROMA_DB_PORT = int(os.getenv('CHROMA_DB_PORT', '8000'))

# ===========================================
# Security (JWT)
# ===========================================
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev_secret_change_in_production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

# Safety thresholds
MEDICAL_CONCERN_THRESHOLD = 0.7 # Confidence threshold for medical concerns
EMERGENCY_THRESHOLD = 0.9 # Threshold for immediate medical referral

# UI settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FONT_FAMILY = "Arial"
FONT_SIZE = 12

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'mindlink.log')

# Disclaimer settings
DISCLAIMER_VISIBLE = True
DISCLAIMER_DURATION = 10 # seconds

# Debug mode
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'