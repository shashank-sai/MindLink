#!/usr/bin/env python3
"""Test the authentication flow."""

import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

print("=" * 60)
print("AUTHENTICATION FLOW TEST")
print("=" * 60)

# Test 1: Database connection
print("\n1. Testing database connection...")
try:
    from config.database import get_db_session
    db_session = get_db_session()
    db_session.execute(text("SELECT 1"))
    print("   ✓ Database connection successful")
except Exception as e:
    print(f"   ✗ Database connection failed: {e}")
    exit(1)

# Test 2: Check if tables exist
print("\n2. Checking required tables...")
required_tables = ['users', 'user_sessions', 'conversations', 'messages', 'user_profiles', 'audit_logs', 'password_reset_tokens']
try:
    from sqlalchemy import inspect
    inspector = inspect(db_session.bind)
    existing_tables = inspector.get_table_names()
    
    for table in required_tables:
        if table in existing_tables:
            print(f"   ✓ Table '{table}' exists")
        else:
            print(f"   ✗ Table '{table}' MISSING - run: python setup_database.py")
except Exception as e:
    print(f"   ✗ Error checking tables: {e}")

# Test 3: Test user registration
print("\n3. Testing user registration...")
try:
    from auth.auth_manager import AuthManager
    auth = AuthManager(db_session)
    
    # Try to register a test user
    test_username = f"test_user_{os.urandom(2).hex()}"
    test_email = f"{test_username}@test.com"
    test_password = "TestPassword123!"
    
    print(f"   Registering user: {test_username}")
    result = auth.register_user(test_username, test_email, test_password)
    print(f"   ✓ Registration successful: {result}")
    
    # Test login
    print("\n4. Testing user login...")
    login_result = auth.login(test_username, test_password)
    print(f"   ✓ Login successful")
    print(f"   User ID: {login_result.get('user_id')}")
    print(f"   Token: {login_result.get('token')[:50]}...")
    
except Exception as e:
    print(f"   ✗ Auth test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
