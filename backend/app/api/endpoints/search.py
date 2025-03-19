from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import DocumentSearchQuery, SearchResponse
from app.services.search import SearchService
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def search_documents(
    search_query: DocumentSearchQuery,
    db: Session = Depends(get_db)
):
    """
    Search for document chunks that match the query.
    """
    try:
        logger.info(f"Performing search with query: '{search_query.query}', limit: {search_query.limit}")
        
        # Search for document chunks that match the query
        results = SearchService.search_documents(
            db=db, 
            query=search_query.query,
            limit=search_query.limit
        )
        
        logger.debug(f"Search found {len(results)} results")
        
        # Return search results
        return {
            "results": results,
            "total": len(results),
            "query": search_query.query
        }
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}",
        ) 