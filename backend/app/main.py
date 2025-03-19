from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.core.logging_config import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_db_client():
    """Initialize database on app startup."""
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        # Don't raise exception here to allow app to start even if DB init fails
        # This allows the app to provide meaningful error messages through the API


@app.get("/")
def root():
    logger.debug("Root endpoint accessed")
    return {"message": "RAG Query API"}
