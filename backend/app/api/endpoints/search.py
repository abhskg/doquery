from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.schemas.document import DocumentSearchQuery, SearchResponse
from app.services.search import SearchService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def search_documents(
    search_query: DocumentSearchQuery,
    db: Session = Depends(get_db)
):
    """
    Search for document chunks that match the query.
    """
    try:
        # Search for document chunks that match the query
        results = SearchService.search_documents(
            db=db, 
            query=search_query.query,
            limit=search_query.limit
        )
        
        # Return search results
        return {
            "results": results,
            "total": len(results),
            "query": search_query.query
        }
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}",
        ) 