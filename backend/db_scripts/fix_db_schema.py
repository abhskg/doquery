#!/usr/bin/env python3
"""
Script to fix database schema issues by dropping and recreating tables.
"""

import logging
import os
import sys

from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from app.db.base import Base
    from app.db.session import SessionLocal, engine
    from app.models.document import Document, DocumentChunk
except ImportError as e:
    logger.error(f"Error importing app modules: {e}")
    sys.exit(1)


def reset_database():
    """Drop all tables and recreate them"""
    try:
        # Check if pgvector extension is installed
        with engine.connect() as conn:
            try:
                result = conn.execute(
                    text(
                        "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                    )
                )
                has_vector = result.scalar()
                if not has_vector:
                    logger.warning(
                        "pgvector extension not found. Attempting to install..."
                    )
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    logger.info("pgvector extension installed")
            except Exception as e:
                logger.error(f"Error checking/installing pgvector: {e}")
                logger.warning("Continuing without pgvector extension")

        # Drop existing tables
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully")

        # Create tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")

        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
            )
            tables = [row[0] for row in result]
            logger.info(f"Tables in database: {tables}")

            # Check document table columns
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'document'"
                )
            )
            columns = [row[0] for row in result]
            logger.info(f"Columns in document table: {columns}")

            # Verify id column exists
            if "id" in columns:
                logger.info(
                    "The 'id' column exists in the document table - schema is correct"
                )
            else:
                logger.error("The 'id' column is still missing in the document table")

        return True
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting database schema fix")

    confirm = input(
        "This will DELETE ALL DATA in the database tables. Are you sure? (y/N): "
    )
    if confirm.lower() != "y":
        logger.info("Operation cancelled")
        sys.exit(0)

    if reset_database():
        logger.info("Database schema fixed successfully")
    else:
        logger.error("Failed to fix database schema")
        sys.exit(1)
