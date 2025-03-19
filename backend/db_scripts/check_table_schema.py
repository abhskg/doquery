#!/usr/bin/env python3
"""
Script to check the actual database schema and compare with expected models.
"""

import logging
import os
import sys

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from app.db.session import SessionLocal, engine
    from app.models.document import Document, DocumentChunk
except ImportError as e:
    logger.error(f"Error importing app modules: {e}")
    sys.exit(1)


def print_column_info(column):
    """Print detailed column information"""
    return {
        "name": column.name,
        "type": str(column.type),
        "nullable": column.nullable,
        "primary_key": column.primary_key,
        "default": str(column.default) if column.default else None,
    }


def check_schema():
    """Check the database schema and compare with SQLAlchemy models"""
    try:
        # Create inspector to examine the database
        inspector = inspect(engine)

        # Get all tables in the database
        tables = inspector.get_table_names()
        logger.info(f"Tables in database: {tables}")

        # Check if document table exists
        if "document" in tables:
            columns = inspector.get_columns("document")
            logger.info("Document table columns:")
            for column in columns:
                logger.info(
                    f"  {column['name']}: {column['type']} (nullable: {column['nullable']})"
                )

            # Get SQLAlchemy model columns
            model_columns = {c.name: c for c in Document.__table__.columns}
            logger.info("SQLAlchemy Document model columns:")
            for name, column in model_columns.items():
                logger.info(f"  {name}: {column.type} (nullable: {column.nullable})")

            # Compare columns
            db_column_names = {c["name"] for c in columns}
            model_column_names = set(model_columns.keys())

            missing_in_db = model_column_names - db_column_names
            if missing_in_db:
                logger.error(
                    f"Columns in model but missing in database: {missing_in_db}"
                )

            extra_in_db = db_column_names - model_column_names
            if extra_in_db:
                logger.warning(f"Columns in database but not in model: {extra_in_db}")
        else:
            logger.error("Document table does not exist in the database")

        # Also check the SQL query directly
        with engine.connect() as conn:
            try:
                result = conn.execute(
                    text(
                        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'document'"
                    )
                )
                rows = result.fetchall()
                logger.info("Document table columns from information_schema:")
                for row in rows:
                    logger.info(f"  {row[0]}: {row[1]}")
            except SQLAlchemyError as e:
                logger.error(f"Error querying information_schema: {e}")

    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting database schema check")
    check_schema()
    logger.info("Schema check completed")
