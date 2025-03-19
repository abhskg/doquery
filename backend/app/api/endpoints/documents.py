import uuid
from typing import Any, Dict, List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import get_db
from app.schemas.document import DocumentChunkResponse, DocumentResponse
from app.services.document import DocumentService

router = APIRouter()
logger = get_logger(__name__)


async def process_document_background(db: Session, document_id: str):
    """Background task for processing documents."""
    try:
        logger.info(f"Starting background processing of document {document_id}")
        document = DocumentService.get_document_by_id(db=db, document_id=document_id)
        if document:
            logger.debug(f"Document {document_id} found, processing...")
            DocumentService.process_document(db=db, document=document)
            logger.info(f"Document {document_id} processed successfully")
        else:
            logger.error(f"Document {document_id} not found for processing")
    except Exception as e:
        logger.error(
            f"Error processing document {document_id}: {str(e)}", exc_info=True
        )


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
        logger.info(f"Document upload started: {file.filename}")

        # Check file size (limit to 10MB for example)
        file_size = 0
        chunk_size = 1024 * 4  # 4KB chunks
        content_chunks = []

        logger.debug(f"Reading file {file.filename} in chunks")
        while chunk := await file.read(chunk_size):
            file_size += len(chunk)
            content_chunks.append(chunk)

            # Check size limit
            if file_size > 100 * 1024 * 1024:  # 100MB
                logger.warning(f"File {file.filename} too large: {file_size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large. Maximum file size is 100MB.",
                )

        # Reset file position
        await file.seek(0)
        logger.debug(f"File size: {file_size} bytes")

        # Read file content
        content = b"".join(content_chunks)

        try:
            content_str = content.decode("utf-8")
            logger.debug(f"Successfully decoded file content as UTF-8")
        except UnicodeDecodeError:
            logger.warning(f"File {file.filename} is not UTF-8 encoded")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File encoding not supported. Please upload a UTF-8 encoded text file.",
            )

        # Create document in database
        logger.debug(f"Creating document record in database for {file.filename}")
        document = DocumentService.create_document(
            db=db,
            filename=file.filename,
            content_type=file.content_type,
            content=content_str,
        )

        # Process document in background
        logger.info(f"Scheduling background processing for document {document.id}")
        background_tasks.add_task(
            process_document_background, db=db, document_id=str(document.id)
        )

        logger.info(
            f"Document {document.id} uploaded successfully, processing scheduled"
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
        logger.error(f"Error processing document upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}",
        )


@router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
async def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all uploaded documents with pagination.
    """
    try:
        logger.info(f"Retrieving documents (skip={skip}, limit={limit})")
        documents = DocumentService.get_all_documents(db=db, skip=skip, limit=limit)
        logger.debug(f"Found {len(documents)} documents")
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
        logger.error(f"Error retrieving documents: {str(e)}", exc_info=True)
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
        logger.info(f"Deleting document {document_id}")
        document = DocumentService.get_document_by_id(
            db=db, document_id=str(document_id)
        )
        if not document:
            logger.warning(f"Document {document_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found",
            )

        DocumentService.delete_document(db=db, document_id=str(document_id))
        logger.info(f"Document {document_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}",
        )


@router.get(
    "/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK
)
async def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a document by ID.
    """
    try:
        logger.info(f"Retrieving document {document_id}")
        document = DocumentService.get_document_by_id(
            db=db, document_id=str(document_id)
        )
        if not document:
            logger.warning(f"Document {document_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found",
            )

        logger.debug(f"Document {document_id} retrieved successfully")
        return {
            "id": document.id,
            "filename": document.filename,
            "status": "Processed" if document.chunk_ids else "Processing",
            "created_at": document.created_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving document {document_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}",
        )


@router.get(
    "/{document_id}/chunks",
    response_model=List[DocumentChunkResponse],
    status_code=status.HTTP_200_OK,
)
async def get_document_chunks(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve all chunks for a document.
    """
    try:
        logger.info(f"Retrieving chunks for document {document_id}")
        document = DocumentService.get_document_by_id(
            db=db, document_id=str(document_id)
        )
        if not document:
            logger.warning(f"Document {document_id} not found when retrieving chunks")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found",
            )

        chunks = DocumentService.get_document_chunks(
            db=db, document_id=str(document_id)
        )
        logger.debug(f"Retrieved {len(chunks)} chunks for document {document_id}")
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
        logger.error(
            f"Error retrieving document chunks for {document_id}: {str(e)}",
            exc_info=True,
        )
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
        logger.info("Running database connection check")
        # Try to execute a simple query to check the connection
        result = db.execute(text("SELECT 1")).scalar()
        logger.debug(f"Database connection check result: {result}")

        # Check if document table exists
        table_exists = db.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'document')"
            )
        ).scalar()
        logger.debug(f"Document table exists: {table_exists}")

        # Get all tables in the database
        tables = (
            db.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
                )
            )
            .scalars()
            .all()
        )
        logger.debug(f"Database tables: {tables}")

        # Check if pgvector extension is installed
        try:
            vector_extension = db.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                )
            ).scalar()
            logger.debug(f"pgvector extension installed: {vector_extension}")
        except Exception as e:
            logger.warning(f"Error checking pgvector extension: {str(e)}")
            vector_extension = False

        # Check database connection details
        db_url = str(db.bind.url).replace(":*****@", "@")  # Hide password
        logger.debug(f"Database URL: {db_url}")

        logger.info("Database check completed")
        return {
            "connection": "success" if result == 1 else "failed",
            "document_table_exists": bool(table_exists),
            "available_tables": tables,
            "pgvector_extension": bool(vector_extension),
            "db_details": db_url,
            "missing_tables": "Document tables not found. Run 'python init_db.py' to create tables."
            if not table_exists
            else None,
            "missing_extensions": "pgvector extension not found. Run 'CREATE EXTENSION vector;' in your PostgreSQL database."
            if not vector_extension
            else None,
        }
    except Exception as e:
        logger.error(f"Error checking database connection: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(e)}",
        )
