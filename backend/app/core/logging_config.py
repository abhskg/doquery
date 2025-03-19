"""Centralized logging configuration for the application."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = "logs"

# Create logs directory if it doesn't exist
Path(LOG_DIR).mkdir(exist_ok=True)


# Configure the root logger
def configure_logging():
    """Configure the root logger with console and file handlers."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))

    # Clear existing handlers to avoid duplicates when reconfiguring
    if root_logger.handlers:
        root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # Create file handler
    log_filename = f"{LOG_DIR}/app-{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # SQLAlchemy logging is very verbose, set it to WARNING level
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return root_logger


# Helper function to get a logger for a module
def get_logger(name):
    """Get a logger with the specified name."""
    return logging.getLogger(name)
