from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


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
        # Implementation will be added later
        pass

    @staticmethod
    def process_document(db: Session, document: Document) -> List[DocumentChunk]:
        """
        Process a document into chunks and create embeddings.
        """
        # Implementation will be added later
        pass

    @staticmethod
    def get_document_by_id(db: Session, document_id: str) -> Optional[Document]:
        """
        Get a document by its ID.
        """
        # Implementation will be added later
        pass
