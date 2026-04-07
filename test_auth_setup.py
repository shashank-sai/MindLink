#!/usr/bin/env python3
"""
Test script for MindLink Authentication and Vector DB setup.
Run this to verify your installation is working correctly.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("MindLink Setup Verification")
print("=" * 60)

# Test 1: Environment Variables
print("\n[1/6] Checking environment variables...")
required_vars = [
    'DATABASE_URL',
    'JWT_SECRET_KEY',
    'OLLAMA_HOST',
    'EMBEDDING_MODEL'
]

missing_vars = []
for var in required_vars:
    if os.getenv(var):
        print(f"  ✓ {var} is set")
    else:
        print(f"  ✗ {var} is missing")
        missing_vars.append(var)

if missing_vars:
    print(f"\n  WARNING: Missing environment variables: {', '.join(missing_vars)}")
    print("  Please update your .env file")
else:
    print("  All required environment variables are set ✓")

# Test 2: Database Connection
print("\n[2/6] Testing database connection...")
try:
    from config.database import db_manager, check_db_connection
    if check_db_connection():
        print("  ✓ Database connection successful")
    else:
        print("  ✗ Database connection failed")
except Exception as e:
    print(f"  ✗ Database error: {e}")

# Test 3: ChromaDB
print("\n[3/6] Testing ChromaDB connection...")
try:
    from vector_store.chroma_client import get_chroma_client
    client = get_chroma_client()
    collections = client.list_collections()
    print(f"  ✓ ChromaDB connected ({len(collections)} collections)")
except Exception as e:
    print(f"  ✗ ChromaDB error: {e}")

# Test 4: Ollama Connection
print("\n[4/6] Testing Ollama connection...")
try:
    import ollama
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    client = ollama.Client(host=ollama_host)
    models = client.list()
    print(f"  ✓ Ollama connected ({len(models.get('models', []))} models)")

    # Check required models
    model_names = [m.get('name') for m in models.get('models', [])]
    required_models = ['phi3:3.8b', 'mistral:7b', 'phi3.5:3.8b', 'nomic-embed-text']
    for model in required_models:
        if any(model in m for m in model_names):
            print(f"    ✓ Model: {model}")
        else:
            print(f"    ✗ Model missing: {model} (run: ollama pull {model})")

except Exception as e:
    print(f"  ✗ Ollama error: {e}")

# Test 5: Embedding Service
print("\n[5/6] Testing embedding service...")
try:
    from vector_store.embedding_service import get_embedding_service
    service = get_embedding_service()
    embedding = service.generate_embedding("test")
    if embedding and len(embedding) > 0:
        print(f"  ✓ Embedding generated (dimension: {len(embedding)})")
    else:
        print("  ✗ Embedding generation failed")
except Exception as e:
    print(f"  ✗ Embedding error: {e}")

# Test 6: Auth Manager
print("\n[6/6] Testing authentication module...")
try:
    from auth.auth_manager import AuthManager
    from db.database import get_db_session

    # Test user creation (will fail if DB not set up)
    auth = AuthManager()
    print("  ✓ AuthManager initialized")

    # Test password hashing
    test_hash, test_salt = auth._hash_password("test_password")
    if test_hash and test_salt:
        print("  ✓ Password hashing works")

    # Test verification
    if auth._verify_password("test_password", test_hash, test_salt):
        print("  ✓ Password verification works")

except Exception as e:
    print(f"  ✗ Auth error: {e}")

# Summary
print("\n" + "=" * 60)
print("Verification Complete")
print("=" * 60)
print("""
Next Steps:
1. If database tests failed: Run 'python setup_database.py'
2. If Ollama tests failed: Ensure Ollama is running and pull required models
3. If embedding tests failed: Check Ollama connection and nomic-embed-text model
4. Run 'python web_app.py' to start the application

For detailed setup instructions, see SETUP_GUIDE.md
""")
