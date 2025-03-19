from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.ml.provider import get_model_provider
from app.models.document import DocumentChunk


class QueryService:
    """
    Service for query operations.
    """

    @staticmethod
    def search_similar_chunks(
        db: Session, query_embedding: List[float], top_k: int = 4
    ) -> List[DocumentChunk]:
        """
        Search for similar document chunks based on vector similarity.
        """
        # Implementation will be added later
        pass

    @staticmethod
    def generate_answer(
        question: str, context_chunks: List[DocumentChunk]
    ) -> Dict[str, Any]:
        """
        Generate an answer using the configured model provider based on the question and context chunks.

        Args:
            question: The user's question
            context_chunks: Document chunks retrieved as context for answering

        Returns:
            Dictionary with the generated answer and metadata
        """
        # Get the configured model provider
        provider = get_model_provider()

        # Combine context chunks into a single context string
        context = "\n\n".join([chunk.content for chunk in context_chunks])

        # Generate completion with the provider
        return provider.generate_completion(
            prompt=question,
            context=context,
            temperature=0.7,  # Moderate creativity
            max_tokens=500,  # Reasonable response length
        )
