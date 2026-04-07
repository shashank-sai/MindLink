#!/usr/bin/env python3
"""
Fix database name case-sensitivity issue.
This script will either:
1. Create a new 'mindlink' database from 'MindLink' if it doesn't exist
2. Or simply verify the connection
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:6155@localhost:5432/mindlink')
DEFAULT_URL = 'postgresql://postgres:6155@localhost:5432/postgres'

print("=" * 60)
print("DATABASE NAME FIX SCRIPT")
print("=" * 60)

try:
    from sqlalchemy import create_engine, text
    
    # Connect to postgres database to manage other databases
    print("\n1. Connecting to PostgreSQL server...")
    engine = create_engine(DEFAULT_URL)
    
    with engine.connect() as conn:
        # Check if 'mindlink' (lowercase) exists
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'mindlink'"))
        mindlink_exists = result.fetchone() is not None
        
        # Check if 'MindLink' (capitalized) exists
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'MindLink'"))
        MindLink_exists = result.fetchone() is not None
        
        print(f"\n2. Database status:")
        print(f"   'mindlink' (lowercase): {'EXISTS' if mindlink_exists else 'NOT FOUND'}")
        print(f"   'MindLink' (capitalized): {'EXISTS' if MindLink_exists else 'NOT FOUND'}")
        
        if mindlink_exists:
            print("\n✓ Database 'mindlink' already exists. No action needed.")
        elif MindLink_exists:
            print("\n3. Fixing: Creating 'mindlink' from 'MindLink'...")
            
            # Close connections to MindLink
            print("   - Closing active connections to 'MindLink'...")
            conn.execute(text("""
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE datname = 'MindLink' AND pid <> pg_backend_pid();
            """))
            
            # Create new database with lowercase name
            print("   - Creating 'mindlink' database...")
            conn.execute(text("CREATE DATABASE mindlink"))
            
            print("   - Note: You may need to run migrations on the new database.")
            print("   - Run: python setup_database.py")
            
        else:
            print("\n✗ Neither 'mindlink' nor 'MindLink' database exists!")
            print("   Creating new 'mindlink' database...")
            conn.execute(text("CREATE DATABASE mindlink"))
            print("   - Run: python setup_database.py")
    
    print("\n" + "=" * 60)
    print("SUCCESS! Please restart the Flask application.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nManual fix:")
    print("1. Open pgAdmin")
    print("2. Right-click on 'Databases' -> 'Create' -> 'Database'")
    print("3. Name it exactly: mindlink (lowercase)")
    print("4. Run migrations: python setup_database.py")
