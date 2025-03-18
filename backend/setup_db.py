#!/usr/bin/env python3
"""
PostgreSQL database setup script for RAG Query API.
This script creates the database and installs the pgvector extension if needed.
"""

import logging
import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import settings
try:
    from app.core.config import settings
except ImportError:
    logger.error("Could not import settings. Make sure you're running this script from the correct directory.")
    sys.exit(1)


def setup_database():
    """
    Set up the PostgreSQL database with pgvector extension.
    """
    # Connect to PostgreSQL server (without specifying a database)
    try:
        # Connect to default 'postgres' database to create our app database
        conn = psycopg2.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if our database exists
        logger.info(f"Checking if database '{settings.POSTGRES_DB}' exists...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'")
        db_exists = cursor.fetchone()
        
        # Create database if it doesn't exist
        if not db_exists:
            logger.info(f"Creating database '{settings.POSTGRES_DB}'...")
            cursor.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
            logger.info(f"Database '{settings.POSTGRES_DB}' created successfully.")
        else:
            logger.info(f"Database '{settings.POSTGRES_DB}' already exists.")
        
        # Close connection to postgres database
        cursor.close()
        conn.close()
        
        # Connect to our app database to set up pgvector
        conn = psycopg2.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if pgvector extension is installed
        logger.info("Checking if pgvector extension is installed...")
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        vector_exists = cursor.fetchone()
        
        # Create pgvector extension if it doesn't exist
        if not vector_exists:
            logger.info("Installing pgvector extension...")
            try:
                cursor.execute("CREATE EXTENSION vector")
                logger.info("pgvector extension installed successfully.")
            except psycopg2.Error as e:
                logger.error(f"Failed to install pgvector extension: {str(e)}")
                logger.error("You may need to install the pgvector extension in your PostgreSQL server first.")
                logger.error("See https://github.com/pgvector/pgvector for installation instructions.")
        else:
            logger.info("pgvector extension is already installed.")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Database setup completed successfully.")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Database setup error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database setup: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Starting database setup...")
    if setup_database():
        logger.info("Database setup successful!")
        
        # Run database initialization to create tables
        logger.info("Now initializing database tables...")
        try:
            from app.db.init_db import init_db
            init_db()
            logger.info("Database tables created successfully!")
        except Exception as e:
            logger.error(f"Error initializing database tables: {str(e)}")
            sys.exit(1)
    else:
        logger.error("Database setup failed.")
        sys.exit(1) 