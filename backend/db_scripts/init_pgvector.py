"""
Initialize the pgvector extension in the PostgreSQL database.
This script should be run once to ensure the pgvector extension is properly installed.
"""

import logging
from sqlalchemy import text
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_pgvector_installed():
    """Check if pgvector extension is installed."""
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
        ).scalar()
        return bool(result)
    except Exception as e:
        logger.error(f"Error checking if pgvector is installed: {str(e)}")
        return False
    finally:
        db.close()

def install_pgvector():
    """Install the pgvector extension."""
    db = SessionLocal()
    try:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        logger.info("pgvector extension installed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error installing pgvector: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def test_cosine_similarity():
    """Test if the pgvector operators work."""
    db = SessionLocal()
    try:
        # Test the <-> operator (vector distance) instead of cosine_similarity function
        result = db.execute(
            text("SELECT 1 - (ARRAY[1,2,3]::float[] <-> ARRAY[4,5,6]::float[]) as similarity")
        ).scalar()
        logger.info(f"Vector operator test result: {result}")
        return True
    except Exception as e:
        logger.error(f"Error testing pgvector operators: {str(e)}")
        return False
    finally:
        db.close()

def reinstall_pgvector():
    """Reinstall the pgvector extension by dropping and recreating it."""
    # First drop the extension
    db = SessionLocal()
    try:
        db.execute(text("DROP EXTENSION IF EXISTS vector CASCADE;"))
        db.commit()
        logger.info("pgvector extension dropped.")
    except Exception as e:
        logger.error(f"Error dropping pgvector extension: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    # Then reinstall it
    return install_pgvector()

def init_pgvector():
    """Initialize the pgvector extension in the database."""
    # Check if pgvector is installed
    if check_pgvector_installed():
        logger.info("pgvector extension is already installed.")
        
        # Verify that cosine_similarity function exists
        logger.info("Verifying cosine_similarity function...")
        if test_cosine_similarity():
            logger.info("pgvector operators are working correctly.")
            return True
        else:
            logger.info("Trying to repair by reinstalling pgvector extension...")
            return reinstall_pgvector()
    else:
        # Install pgvector
        logger.info("Installing pgvector extension...")
        return install_pgvector()

if __name__ == "__main__":
    logger.info("Initializing pgvector extension...")
    success = init_pgvector()
    
    if success:
        # Verify one more time
        if test_cosine_similarity():
            logger.info("pgvector extension is now properly installed and working.")
        else:
            logger.error("pgvector extension is installed but the pgvector operators are still not working.")
            logger.error("You may need to check your PostgreSQL installation and make sure you have the correct version of pgvector.")
    else:
        logger.error("Failed to initialize pgvector extension.")
        
    logger.info("Done.") 