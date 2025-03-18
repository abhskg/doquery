from fastapi import APIRouter

from app.api.endpoints import documents, queries, guidelines

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(guidelines.router, prefix="/guidelines", tags=["guidelines"])
