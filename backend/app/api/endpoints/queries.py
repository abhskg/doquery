from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.services.search import SearchService
from app.ml.provider import get_model_provider
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=QueryResponse)
async def query_documents(
    query: QueryRequest = Body(...),
    db: Session = Depends(get_db),
):
    """
    Query against embedded documents and return AI-generated answers.
    """
    try:
        logger.info(f"Processing query: '{query.question}'")
        
        # Get the model provider for embeddings
        model_provider = get_model_provider()
        # Step 1: Search for relevant document chunks using the search service
        relevant_chunks = SearchService.search_documents(
            db=db, 
            query=query.question, 
            limit=query.top_k
        )
        
        if not relevant_chunks:
            logger.warning(f"No relevant documents found for query: '{query.question}'")
            return QueryResponse(
                question=query.question,
                answer="I couldn't find any relevant information to answer your question.",
                sources=[]
            )
        
        # Step 2: Extract content from chunks to use as context
        contexts = [chunk["content"] for chunk in relevant_chunks]
        
        # Step 3: Generate a combined context string
        combined_context = "\n\n".join(contexts)
        
        # Step 4: Create a system prompt to ensure the model only uses provided context
        system_prompt = """You are a helpful assistant answering questions based on the provided document chunks.
                        Only use information from the provided context to answer the question.
                        If the context doesn't contain the information needed to answer the question, say so clearly.
                        Do not make up or infer information that is not explicitly stated in the context. 
                        Also provide clear and concise answers with a single line response if its a simple question, without much meandering around the question."""
        
        # Step 4: Use the model to generate an answer based on the question and context
        completion_result = model_provider.generate_completion(
            prompt=query.question,
            context=combined_context,
            temperature=0.7,
            max_tokens=500
        )
        
        # Step 5: Prepare the sources information
        sources = [f"{chunk['document_filename']} (Chunk {chunk['chunk_index'] + 1})" for chunk in relevant_chunks]
        
        # Step 6: Return the response
        return QueryResponse(
            question=query.question,
            answer=completion_result.get("text", "Unable to generate an answer."),
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
