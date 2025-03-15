from typing import List
from openai import OpenAI

from app.core.config import settings


class EmbeddingUtil:
    """
    Utility for generating embeddings.
    """
    
    @staticmethod
    def get_embedding(text: str) -> List[float]:
        """
        Get embedding for a text using OpenAI's embedding model.
        """
        # Implementation will be added later
        pass
    
    @staticmethod
    def get_embeddings(texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts.
        """
        # Implementation will be added later
        pass 