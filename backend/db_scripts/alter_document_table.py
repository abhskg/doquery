#!/usr/bin/env python3
"""
Script to check and fix document table column names without dropping tables.
"""

import logging
import os
import sys

from sqlalchemy import inspect, text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from app.db.session import engine
    from app.models.document import Document
except ImportError as e:
    logger.error(f"Error importing app modules: {e}")
    sys.exit(1)


def check_columns():
    """Check document table columns and rename if needed"""
    try:
        inspector = inspect(engine)

        # Get tables
        tables = inspector.get_table_names()
        logger.info(f"Tables in database: {tables}")

        if "document" not in tables:
            logger.error("Document table doesn't exist in the database")
            return False

        # Get model's column names
        expected_columns = {c.name.lower(): c.name for c in Document.__table__.columns}
        logger.info(f"Expected columns from model: {list(expected_columns.values())}")

        # Get existing column names
        existing_columns = []
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'document'"
                )
            )
            existing_columns = [row[0] for row in result]
            logger.info(f"Existing columns in database: {existing_columns}")

        # Check if id column exists (case-insensitive check)
        id_exists = False
        id_column_name = None
        for col in existing_columns:
            if col.lower() == "id":
                id_exists = True
                id_column_name = col
                break

        if not id_exists:
            logger.error("No column matching 'id' found (case-insensitive)")
            return False

        # If id column name is not exactly 'id', rename it
        if id_column_name != "id":
            logger.warning(
                f"Found column '{id_column_name}' instead of 'id', attempting to rename..."
            )

            # Attempt to rename the column
            with engine.connect() as conn:
                # Using a transaction in case something goes wrong
                with conn.begin():
                    conn.execute(
                        text(
                            f'ALTER TABLE document RENAME COLUMN "{id_column_name}" TO id'
                        )
                    )
                    logger.info(f"Column renamed from '{id_column_name}' to 'id'")

            # Verify the rename worked
            with engine.connect() as conn:
                result = conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = 'document' AND column_name = 'id'"
                    )
                )
                if result.scalar():
                    logger.info("Column renamed successfully")
                else:
                    logger.error("Failed to rename column")
                    return False
        else:
            logger.info("The 'id' column already exists with correct case")

        # Check for other column name mismatches and report them
        for model_col_lower, model_col in expected_columns.items():
            if model_col_lower != "id":  # We already handled id
                col_exists = False
                actual_col_name = None

                for db_col in existing_columns:
                    if db_col.lower() == model_col_lower:
                        col_exists = True
                        actual_col_name = db_col
                        break

                if not col_exists:
                    logger.error(
                        f"Column '{model_col}' from model not found in database (case-insensitive)"
                    )
                elif actual_col_name != model_col:
                    logger.warning(
                        f"Column case mismatch: model has '{model_col}', database has '{actual_col_name}'"
                    )

        return True
    except Exception as e:
        logger.error(f"Error checking columns: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting database column check")
    if check_columns():
        logger.info("Column check completed")
    else:
        logger.error("Column check failed")
        sys.exit(1)
