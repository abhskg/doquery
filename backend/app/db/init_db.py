"""Database initialization script."""

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.base import Base
from app.db.session import engine

logger = get_logger(__name__)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    try:
        logger.info("Starting database initialization")

        # Create tables
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Log database connection details
        db_url = str(engine.url).replace(":*****@", "@")  # Hide password
        logger.info(f"Database connection details: {db_url}")

        # Check for pgvector extension
        with engine.connect() as conn:
            try:
                # Use text() to create a properly executable SQL statement
                logger.debug("Checking for pgvector extension")
                result = conn.execute(
                    text(
                        "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                    )
                )
                if result.scalar():
                    logger.info("pgvector extension is installed")
                else:
                    logger.warning(
                        "pgvector extension is not installed. Vector search will not work properly."
                    )
                    logger.info(
                        "You can install pgvector with 'CREATE EXTENSION vector;' in your PostgreSQL database."
                    )
            except ProgrammingError as e:
                logger.warning(f"Error checking pgvector extension: {str(e)}")
                logger.warning(
                    "pgvector extension not found. Vector search may not work properly."
                )
                logger.info(
                    "You can install pgvector with 'CREATE EXTENSION vector;' in your PostgreSQL database."
                )

        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Initialize logging through our config module
    logger.info("Initializing database from command line...")
    init_db()
    logger.info("Database initialization script completed")
