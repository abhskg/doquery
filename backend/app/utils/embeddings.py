from typing import List

from app.ml.provider import get_model_provider


class EmbeddingUtil:
    """
    Utility for generating embeddings.
    """

    @staticmethod
    def get_embedding(text: str) -> List[float]:
        """
        Get embedding for a text using the configured model provider.

        Args:
            text: Text to embed

        Returns:
            Vector embedding as a list of floats
        """
        # Get the appropriate model provider based on configuration
        provider = get_model_provider()

        # Generate the embedding
        return provider.get_embedding(text)

    @staticmethod
    def get_embeddings(texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts using the configured model provider.

        Args:
            texts: List of texts to embed

        Returns:
            List of vector embeddings
        """
        # Get the appropriate model provider based on configuration
        provider = get_model_provider()

        # Generate embeddings for all texts
        return provider.get_embeddings(texts)
