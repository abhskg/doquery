"""Base classes for model providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ModelProvider(ABC):
    """Base class for model providers."""

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a given text.

        Args:
            text: The text to generate an embedding for

        Returns:
            A list of floats representing the embedding vector
        """
        pass

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        context: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        """
        Generate a completion response based on the prompt and optional context.

        Args:
            prompt: The input prompt or question
            context: Optional context to inform the completion
            temperature: Controls randomness of output (0.0-1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Dictionary with completion text and any additional metadata
        """
        pass
