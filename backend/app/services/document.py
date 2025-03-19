from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import cast

from app.core.config import settings
from app.core.logging_config import get_logger
from app.ml.provider import get_model_provider
from app.models.document import Document, DocumentChunk
from app.utils.text_splitter import TextSplitter
from app.utils.tokenizer import Tokenizer

logger = get_logger(__name__)


class DocumentService:
    """
    Service for document operations.
    """

    @staticmethod
    def create_document(
        db: Session, filename: str, content_type: str, content: str
    ) -> Document:
        """
        Create a new document in the database.
        """
        logger.info(f"Creating document record for file: {filename}")
        document = Document(
            filename=filename,
            content_type=content_type,
            content=content,
            chunk_ids=[],
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.debug(f"Document created with ID: {document.id}")
        return document

    @staticmethod
    def process_document(db: Session, document: Document) -> List[DocumentChunk]:
        """
        Process a document into chunks and create embeddings.
        """
        logger.info(
            f"Processing document: {document.id}, filename: {document.filename}"
        )

        # Use the text splitter for better chunking
        logger.debug(
            f"Splitting document content into chunks (size: {len(document.content)} characters)"
        )
        text_splitter = TextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(document.content)
        logger.debug(f"Document split into {len(chunks)} chunks")

        # Get model provider for embedding
        logger.debug("Getting model provider for embeddings")
        model_provider = get_model_provider()

        # Initialize tokenizer for accurate token counting
        logger.debug("Counting tokens in chunks")
        tokenizer = Tokenizer(settings.EMBEDDING_MODEL)
        token_counts = tokenizer.count_tokens(chunks)
        logger.debug(
            f"Token counts calculated: {sum(token_counts) if isinstance(token_counts, list) else 0} total tokens"
        )

        # Create document chunks with embeddings
        document_chunks = []
        chunk_ids = []

        # For better performance, get all embeddings at once
        logger.debug("Generating embeddings for all chunks")
        embeddings = model_provider.get_embeddings(chunks)
        logger.debug(f"Generated {len(embeddings)} embeddings")

        logger.debug("Creating document chunk records")
        for i, (chunk_text, embedding, token_count) in enumerate(
            zip(chunks, embeddings, token_counts)
        ):
            # Create chunk
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
                token_count=token_count,
            )

            db.add(chunk)
            db.flush()  # Flush to get the ID

            document_chunks.append(chunk)
            chunk_ids.append(chunk.id)

        # Update document with chunk IDs
        logger.debug(f"Updating document with {len(chunk_ids)} chunk IDs")
        document.chunk_ids = chunk_ids
        db.commit()

        # Refresh all objects
        for chunk in document_chunks:
            db.refresh(chunk)
        db.refresh(document)

        logger.info(
            f"Document {document.id} processing completed with {len(document_chunks)} chunks"
        )
        return document_chunks

    @staticmethod
    def get_document_by_id(db: Session, document_id: str) -> Optional[Document]:
        """
        Get a document by its ID.
        """
        logger.debug(f"Retrieving document with ID: {document_id}")
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            logger.debug(f"Document {document_id} found")
        else:
            logger.debug(f"Document {document_id} not found")
        return document

    @staticmethod
    def get_all_documents(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        Get all documents with pagination.
        """
        logger.debug(
            f"Retrieving all documents with pagination (skip={skip}, limit={limit})"
        )
        documents = (
            db.query(Document)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Retrieved {len(documents)} documents")
        return documents

    @staticmethod
    def delete_document(db: Session, document_id: str) -> bool:
        """
        Delete a document and its chunks by ID.
        """
        logger.info(f"Deleting document with ID: {document_id}")

        # Delete related chunks first
        logger.debug(f"Deleting chunks for document {document_id}")
        chunks_deleted = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .delete()
        )
        logger.debug(f"Deleted {chunks_deleted} chunks")

        # Delete the document
        logger.debug(f"Deleting document {document_id}")
        result = db.query(Document).filter(Document.id == document_id).delete()
        db.commit()

        logger.info(
            f"Document {document_id} {'deleted successfully' if result > 0 else 'not found'}"
        )
        return result > 0

    @staticmethod
    def get_document_chunks(db: Session, document_id: str) -> List[DocumentChunk]:
        """
        Get all chunks for a document.
        """
        logger.debug(f"Retrieving chunks for document {document_id}")
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
        logger.debug(f"Retrieved {len(chunks)} chunks for document {document_id}")
        return chunks
