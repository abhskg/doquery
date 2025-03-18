"""Database initialization script."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        # Log database connection details
        db_url = str(engine.url).replace(":*****@", "@")  # Hide password
        logger.info(f"Database connection details: {db_url}")
        
        # Check for pgvector extension
        with engine.connect() as conn:
            try:
                # Use text() to create a properly executable SQL statement
                result = conn.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"))
                if result.scalar():
                    logger.info("pgvector extension is installed")
                else:
                    logger.warning("pgvector extension is not installed. Vector search will not work properly.")
                    logger.info("You can install pgvector with 'CREATE EXTENSION vector;' in your PostgreSQL database.")
            except ProgrammingError as e:
                logger.warning(f"Error checking pgvector extension: {str(e)}")
                logger.warning("pgvector extension not found. Vector search may not work properly.")
                logger.info("You can install pgvector with 'CREATE EXTENSION vector;' in your PostgreSQL database.")
        
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


if __name__ == "__main__":
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization script completed") 