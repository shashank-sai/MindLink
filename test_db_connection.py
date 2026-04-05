#!/usr/bin/env python3
"""Test database connection and check for case-sensitivity issues."""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

# Show environment variables
print("\n1. Environment Variables:")
print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")
print(f"   DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")

# Try to connect
print("\n2. Testing PostgreSQL Connection...")
try:
    from sqlalchemy import create_engine, text, inspect
    
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:6155@localhost:5432/mindlink')
    print(f"   Connecting to: {database_url[:50]}...")
    
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Check connection
        result = conn.execute(text("SELECT 1"))
        print("   ✓ Connection successful!")
        
        # List all databases
        print("\n3. Available Databases:")
        result = conn.execute(text("""
            SELECT datname FROM pg_database 
            WHERE datistemplate = false 
            ORDER BY datname;
        """))
        for row in result:
            print(f"   - {row[0]}")
        
        # Check if 'mindlink' or 'MindLink' exists
        print("\n4. Checking for MindLink database variants:")
        for db_name in ['mindlink', 'MindLink', 'MINDLINK']:
            try:
                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
                if result.fetchone():
                    print(f"   ✓ '{db_name}' exists")
                else:
                    print(f"   ✗ '{db_name}' does not exist")
            except Exception as e:
                print(f"   ✗ Error checking '{db_name}': {e}")
        
        # Check tables in the current database
        print("\n5. Tables in current database:")
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if tables:
                for table in tables:
                    print(f"   - {table}")
            else:
                print("   No tables found!")
        except Exception as e:
            print(f"   Error listing tables: {e}")
            
except Exception as e:
    print(f"   ✗ Connection failed: {e}")

print("\n" + "=" * 60)
