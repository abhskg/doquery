"""Search service for document querying and retrieval."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
import logging

from app.models.document import Document, DocumentChunk
from app.ml.provider import get_model_provider

logger = logging.getLogger(__name__)


class SearchService:
    """Service for search operations."""
    
    @staticmethod
    def search_documents(db: Session, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for document chunks that match the query using vector similarity.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of document chunks with similarity scores
        """
        try:
            # Get model provider for embedding the query
            model_provider = get_model_provider()
            
            # Get query embedding
            query_embedding = model_provider.get_embedding(query)
            
            # First, check if the pgvector extension is available
            pgvector_check = db.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")).scalar()
            if not pgvector_check:
                # Fallback to simpler search if pgvector is not available
                return SearchService._fallback_search(db, query, limit)
            
            # Try to use the cosine_similarity function from pgvector
            try:
                # Query to find chunks with similar embeddings
                chunks_with_similarity = (
                    db.query(
                        DocumentChunk,
                        Document.filename.label("document_filename"),
                        func.cosine_similarity(
                            DocumentChunk.embedding, 
                            cast(query_embedding, ARRAY(FLOAT))
                        ).label("similarity"),
                    )
                    .join(Document, DocumentChunk.document_id == Document.id)
                    .order_by(func.cosine_similarity(
                        DocumentChunk.embedding, 
                        cast(query_embedding, ARRAY(FLOAT))
                    ).desc())
                    .limit(limit)
                    .all()
                )
                
                # Format results
                results = []
                for chunk, filename, similarity in chunks_with_similarity:
                    results.append({
                        "document_id": chunk.document_id,
                        "chunk_id": chunk.id,
                        "document_filename": filename,
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "similarity": float(similarity) if similarity is not None else 0.0,
                    })
                
                return results
            except Exception as e:
                logger.error(f"Error using cosine_similarity function: {str(e)}")
                # If cosine_similarity function call fails, try fallback
                return SearchService._fallback_search(db, query, limit)
                
        except Exception as e:
            # Log the error
            logger.error(f"Error in vector search: {str(e)}")
            
            # Return empty results or fallback
            return []
    
    @staticmethod
    def _fallback_search(db: Session, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fallback search method using text similarity when vector search is unavailable"""
        logger.info("Using fallback text search method")
        # Simple text search fallback
        query_lower = query.lower()
        
        # Get all chunks and sort them by simple text matching
        chunks = (
            db.query(DocumentChunk, Document.filename.label("document_filename"))
            .join(Document, DocumentChunk.document_id == Document.id)
            .all()
        )
        
        # Score chunks based on text similarity (simple contains check)
        scored_chunks = []
        for chunk, filename in chunks:
            content_lower = chunk.content.lower()
            # Basic relevance score based on whether the content contains query terms
            if query_lower in content_lower:
                # Calculate a simple similarity score based on term frequency
                similarity = content_lower.count(query_lower) / len(content_lower)
                scored_chunks.append((chunk, filename, similarity))
        
        # Sort by similarity score and limit results
        scored_chunks.sort(key=lambda x: x[2], reverse=True)
        results = []
        
        for chunk, filename, similarity in scored_chunks[:limit]:
            results.append({
                "document_id": chunk.document_id,
                "chunk_id": chunk.id,
                "document_filename": filename,
                "content": chunk.content,
                "chunk_index": chunk.chunk_index,
                "similarity": float(similarity),
            })
        
        return results 