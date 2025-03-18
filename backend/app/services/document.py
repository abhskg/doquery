from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT

from app.models.document import Document, DocumentChunk
from app.ml.provider import get_model_provider
from app.utils.text_splitter import TextSplitter
from app.utils.tokenizer import Tokenizer
from app.core.config import settings


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
        document = Document(
            filename=filename,
            content_type=content_type,
            content=content,
            chunk_ids=[],
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def process_document(db: Session, document: Document) -> List[DocumentChunk]:
        """
        Process a document into chunks and create embeddings.
        """
        # Use the text splitter for better chunking
        text_splitter = TextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(document.content)
        
        # Get model provider for embedding
        model_provider = get_model_provider()
        
        # Initialize tokenizer for accurate token counting
        tokenizer = Tokenizer(settings.EMBEDDING_MODEL)
        token_counts = tokenizer.count_tokens(chunks)
        
        # Create document chunks with embeddings
        document_chunks = []
        chunk_ids = []
        
        # For better performance, get all embeddings at once
        embeddings = model_provider.get_embeddings(chunks)
        
        for i, (chunk_text, embedding, token_count) in enumerate(zip(chunks, embeddings, token_counts)):
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
        document.chunk_ids = chunk_ids
        db.commit()
        
        # Refresh all objects
        for chunk in document_chunks:
            db.refresh(chunk)
        db.refresh(document)
        
        return document_chunks

    @staticmethod
    def get_document_by_id(db: Session, document_id: str) -> Optional[Document]:
        """
        Get a document by its ID.
        """
        return db.query(Document).filter(Document.id == document_id).first()
    
    @staticmethod
    def get_all_documents(db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        Get all documents with pagination.
        """
        return db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_document(db: Session, document_id: str) -> bool:
        """
        Delete a document and its chunks by ID.
        """
        # Delete related chunks first
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        
        # Delete the document
        result = db.query(Document).filter(Document.id == document_id).delete()
        db.commit()
        
        return result > 0
    
    @staticmethod
    def get_document_chunks(db: Session, document_id: str) -> List[DocumentChunk]:
        """
        Get all chunks for a document.
        """
        return db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index).all()
    
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
        # Get model provider for embedding the query
        model_provider = get_model_provider()
        
        # Get query embedding
        query_embedding = model_provider.get_embedding(query)
        
        # Convert the query embedding to the format needed for PostgreSQL's vector similarity search
        # This uses the pgvector extension which must be installed in the database
        
        # Get the most similar chunks using cosine similarity
        # Note: This requires the pgvector extension to be installed in PostgreSQL
        # and the embedding column to be of type vector
        # The actual SQL would look something like:
        # SELECT dc.*, d.filename, (dc.embedding <=> query_embedding) AS similarity
        # FROM document_chunk dc
        # JOIN document d ON dc.document_id = d.id
        # ORDER BY similarity
        # LIMIT limit
        
        # For now, we'll implement a simple approach (PostgreSQL with pgvector implementation)
        # This assumes you have the PostgreSQL database with pgvector extension set up
        
        # Import SQLAlchemy functions for vector operations
        
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
                "similarity": float(similarity),  # Convert to Python float
            })
        
        return results
