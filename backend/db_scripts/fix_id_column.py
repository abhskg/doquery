#!/usr/bin/env python3
"""
Script to specifically check and fix the 'id' column in the document table.
"""

import logging
import os
import sys
import uuid

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
except ImportError as e:
    logger.error(f"Error importing app modules: {e}")
    sys.exit(1)


def fix_id_column():
    """Check if id column exists in document table and create it if missing"""
    try:
        inspector = inspect(engine)

        # Check if document table exists
        tables = inspector.get_table_names()
        if "document" not in tables:
            logger.error("Document table doesn't exist in the database")
            return False

        # Get existing column names in document table
        existing_columns = []
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'document'"
                )
            )
            existing_columns = [row[0] for row in result]
            logger.info(f"Existing columns in document table: {existing_columns}")

        # Check if 'id' column exists (case-sensitive)
        if "id" in existing_columns:
            logger.info("The 'id' column already exists in the document table")
            return True

        # Check for a UUID primary key column with a different name
        primary_key_columns = []
        uuid_columns = []

        for column_name in existing_columns:
            col_info = inspector.get_columns("document")
            for col in col_info:
                if col["name"] == column_name:
                    # Check if the column is a primary key
                    pk_constraint = inspector.get_pk_constraint("document")
                    if (
                        "constrained_columns" in pk_constraint
                        and column_name in pk_constraint["constrained_columns"]
                    ):
                        primary_key_columns.append(column_name)

                    # Check if it's a UUID column
                    col_type = str(col["type"]).lower()
                    if "uuid" in col_type:
                        uuid_columns.append(column_name)

                    break

        logger.info(f"Primary key columns: {primary_key_columns}")
        logger.info(f"UUID columns: {uuid_columns}")

        # If we found a UUID primary key column with a different name
        pk_uuid_columns = list(set(primary_key_columns) & set(uuid_columns))
        if pk_uuid_columns:
            column_to_rename = pk_uuid_columns[0]
            logger.info(
                f"Found primary key UUID column '{column_to_rename}', will rename to 'id'"
            )

            # Rename the column to 'id'
            with engine.connect() as conn:
                with conn.begin():
                    conn.execute(
                        text(
                            f'ALTER TABLE document RENAME COLUMN "{column_to_rename}" TO "id"'
                        )
                    )
                    logger.info(f"Column '{column_to_rename}' renamed to 'id'")

            # Verify the rename worked
            with engine.connect() as conn:
                result = conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = 'document' AND column_name = 'id'"
                    )
                )
                if result.scalar():
                    logger.info("Column renamed successfully")
                    return True
                else:
                    logger.error("Failed to rename column")
                    return False

        # If no suitable column to rename, we need to add a new id column
        logger.warning(
            "No suitable UUID primary key column found. Creating new 'id' column."
        )

        with engine.connect() as conn:
            with conn.begin():
                # Add id column
                conn.execute(text('ALTER TABLE document ADD COLUMN "id" UUID'))
                logger.info("Added 'id' column to document table")

                # Generate random UUIDs for existing rows
                conn.execute(text('UPDATE document SET "id" = gen_random_uuid()'))
                logger.info("Generated UUIDs for existing rows")

                # Make id column NOT NULL
                conn.execute(
                    text('ALTER TABLE document ALTER COLUMN "id" SET NOT NULL')
                )
                logger.info("Set 'id' column to NOT NULL")

                # Make id column the primary key
                # First, check if a primary key constraint already exists and drop it
                pk_constraint = inspector.get_pk_constraint("document")
                if pk_constraint and "name" in pk_constraint and pk_constraint["name"]:
                    conn.execute(
                        text(
                            f"ALTER TABLE document DROP CONSTRAINT IF EXISTS \"{pk_constraint['name']}\""
                        )
                    )
                    logger.info(
                        f"Dropped existing primary key constraint: {pk_constraint['name']}"
                    )

                # Add the primary key constraint
                conn.execute(text('ALTER TABLE document ADD PRIMARY KEY ("id")'))
                logger.info("Set 'id' column as primary key")

        # Verify the change worked
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'document' AND column_name = 'id'"
                )
            )
            if result.scalar():
                logger.info("ID column added successfully")
                return True
            else:
                logger.error("Failed to add ID column")
                return False

    except Exception as e:
        logger.error(f"Error fixing id column: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting ID column fix")
    if fix_id_column():
        logger.info("ID column fix completed successfully")
    else:
        logger.error("ID column fix failed")
        sys.exit(1)
