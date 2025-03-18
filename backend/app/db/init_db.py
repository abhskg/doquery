"""Database initialization script."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError

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
        
        # Check for pgvector extension
        with engine.connect() as conn:
            try:
                conn.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN 1 ELSE 0 END")
                logger.info("pgvector extension check completed")
            except ProgrammingError:
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