from fastapi import APIRouter

from app.api.endpoints import documents, guidelines, queries, search

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(guidelines.router, prefix="/guidelines", tags=["guidelines"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
