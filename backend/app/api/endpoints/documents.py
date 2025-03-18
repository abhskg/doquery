from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import uuid
import logging
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.document import DocumentResponse, DocumentChunkResponse
from app.services.document import DocumentService

router = APIRouter()
logger = logging.getLogger(__name__)


async def process_document_background(db: Session, document_id: str):
    """Background task for processing documents."""
    try:
        document = DocumentService.get_document_by_id(db=db, document_id=document_id)
        if document:
            DocumentService.process_document(db=db, document=document)
            logger.info(f"Document {document_id} processed successfully")
        else:
            logger.error(f"Document {document_id} not found for processing")
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a document to be processed and embedded.
    """
    try:
        # Check file size (limit to 10MB for example)
        file_size = 0
        chunk_size = 1024 * 4  # 4KB chunks
        content_chunks = []
        
        while chunk := await file.read(chunk_size):
            file_size += len(chunk)
            content_chunks.append(chunk)
            
            # Check size limit
            if file_size > 100 * 1024 * 1024:  # 100MB
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large. Maximum file size is 100MB.",
                )
        
        # Reset file position
        await file.seek(0)
        
        # Read file content
        content = b"".join(content_chunks)
        
        try:
            content_str = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File encoding not supported. Please upload a UTF-8 encoded text file.",
            )
        
        # Create document in database
        document = DocumentService.create_document(
            db=db,
            filename=file.filename,
            content_type=file.content_type,
            content=content_str,
        )
        
        # Process document in background
        background_tasks.add_task(
            process_document_background, db=db, document_id=str(document.id)
        )
        
        return {
            "id": document.id,
            "filename": document.filename,
            "status": "Document uploaded and processing started",
            "created_at": document.created_at,
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing document upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}",
        )


@router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
async def get_documents(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all uploaded documents with pagination.
    """
    try:
        documents = DocumentService.get_all_documents(db=db, skip=skip, limit=limit)
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "status": "Processed" if doc.chunk_ids else "Processing",
                "created_at": doc.created_at,
            }
            for doc in documents
        ]
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}",
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a document by ID.
    """
    try:
        document = DocumentService.get_document_by_id(db=db, document_id=str(document_id))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found",
            )
        
        DocumentService.delete_document(db=db, document_id=str(document_id))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}",
        )


@router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a document by ID.
    """
    try:
        document = DocumentService.get_document_by_id(db=db, document_id=str(document_id))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found",
            )
        
        return {
            "id": document.id,
            "filename": document.filename,
            "status": "Processed" if document.chunk_ids else "Processing",
            "created_at": document.created_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}",
        )

@router.get("/{document_id}/chunks", response_model=List[DocumentChunkResponse], status_code=status.HTTP_200_OK)
async def get_document_chunks(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve all chunks for a document.
    """
    try:
        document = DocumentService.get_document_by_id(db=db, document_id=str(document_id))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found",
            )
        
        chunks = DocumentService.get_document_chunks(db=db, document_id=str(document_id))
        return [
            {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "token_count": chunk.token_count,
                "created_at": chunk.created_at,
            }
            for chunk in chunks
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document chunks for {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document chunks: {str(e)}",
        )

@router.get("/db-check", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def check_db_connection(db: Session = Depends(get_db)):
    """
    Check the database connection and tables.
    """
    try:
        # Try to execute a simple query to check the connection
        result = db.execute(text("SELECT 1")).scalar()
        
        # Check if document table exists
        table_exists = db.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'document')")
        ).scalar()
        
        # Get all tables in the database
        tables = db.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        ).scalars().all()
        
        # Check if pgvector extension is installed
        try:
            vector_extension = db.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            ).scalar()
        except Exception as e:
            logger.warning(f"Error checking pgvector extension: {str(e)}")
            vector_extension = False
        
        # Check database connection details
        db_url = str(db.bind.url).replace(":*****@", "@")  # Hide password
        
        return {
            "connection": "success" if result == 1 else "failed",
            "document_table_exists": bool(table_exists),
            "available_tables": tables,
            "pgvector_extension": bool(vector_extension),
            "db_details": db_url,
            "missing_tables": "Document tables not found. Run 'python init_db.py' to create tables." if not table_exists else None,
            "missing_extensions": "pgvector extension not found. Run 'CREATE EXTENSION vector;' in your PostgreSQL database." if not vector_extension else None
        }
    except Exception as e:
        logger.error(f"Error checking database connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(e)}",
        )    
