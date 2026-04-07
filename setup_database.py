#!/usr/bin/env python3
"""
Database Setup Script for MindLink.
Initializes PostgreSQL database with required schema.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://mindlink_user:password@localhost:5432/mindlink')


def check_postgresql_connection():
    """Check if PostgreSQL is accessible."""
    try:
        import psycopg2
        from psycopg2 import sql

        # Try to connect to PostgreSQL server (without database)
        server_url = DATABASE_URL.rsplit('/', 1)[0]  # Remove database name
        conn = psycopg2.connect(
            f"{server_url}/postgres",
            connect_timeout=5
        )
        conn.close()
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return False


def create_database():
    """Create the database if it doesn't exist."""
    try:
        import psycopg2
        from psycopg2 import sql

        # Connect to PostgreSQL server (without database)
        server_url = DATABASE_URL.rsplit('/', 1)[0]
        db_name = DATABASE_URL.rsplit('/', 1)[1].split('?')[0]

        conn = psycopg2.connect(f"{server_url}/postgres")
        conn.autocommit = True
        cur = conn.cursor()

        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if not cur.fetchone():
            logger.info(f"Creating database: {db_name}")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            logger.info(f"Database {db_name} created successfully")
        else:
            logger.info(f"Database {db_name} already exists")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False


def run_migrations():
    """Run SQL migrations."""
    try:
        import psycopg2

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Read migration file
        migration_path = Path(__file__).parent / 'db' / 'migrations' / '001_initial_schema.sql'
        if not migration_path.exists():
            logger.error("Migration file not found: 001_initial_schema.sql")
            return False

        with open(migration_path, 'r') as f:
            migration_sql = f.read()

        logger.info("Running database migrations...")
        cur.execute(migration_sql)
        conn.commit()
        cur.close()
        conn.close()

        logger.info("Database migrations completed successfully")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def test_connection():
    """Test database connection after setup."""
    try:
        from sqlalchemy import text
        from config.database import get_db_session

        session = get_db_session()
        session.execute(text("SELECT 1"))
        session.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("=" * 50)
    logger.info("MindLink Database Setup")
    logger.info("=" * 50)

    # Step 1: Check PostgreSQL connection
    logger.info("\nStep 1: Checking PostgreSQL connection...")
    if not check_postgresql_connection():
        logger.error("PostgreSQL is not running or not accessible.")
        logger.error("Please ensure PostgreSQL is installed and running.")
        logger.error("You can also use the Docker setup:")
        logger.error("  docker run -d --name mindlink-postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15")
        return False

    logger.info("PostgreSQL connection successful ✓")

    # Step 2: Create database
    logger.info("\nStep 2: Creating database...")
    if not create_database():
        logger.error("Failed to create database")
        return False

    logger.info("Database ready ✓")

    # Step 3: Run migrations
    logger.info("\nStep 3: Running migrations...")
    if not run_migrations():
        logger.error("Failed to run migrations")
        return False

    logger.info("Migrations complete ✓")

    # Step 4: Test connection
    logger.info("\nStep 4: Testing connection...")
    if not test_connection():
        logger.error("Connection test failed")
        return False

    logger.info("\n" + "=" * 50)
    logger.info("Database setup completed successfully! ✓")
    logger.info("=" * 50)
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
