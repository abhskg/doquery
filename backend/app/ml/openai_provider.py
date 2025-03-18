"""OpenAI model provider implementation."""

from typing import List, Dict, Any
import tiktoken
from openai import OpenAI

from app.core.config import settings
from app.ml.base import ModelProvider


class OpenAIProvider(ModelProvider):
    """OpenAI model provider implementation."""

    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = settings.EMBEDDING_MODEL
        self.completion_model = settings.COMPLETION_MODEL

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a given text using OpenAI.

        Args:
            text: The text to generate an embedding for

        Returns:
            A list of floats representing the embedding vector
        """
        response = self.client.embeddings.create(
            model=self.embedding_model, input=text, encoding_format="float"
        )
        return response.data[0].embedding

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using OpenAI.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        response = self.client.embeddings.create(
            model=self.embedding_model, input=texts, encoding_format="float"
        )
        return [data.embedding for data in response.data]

    def generate_completion(
        self,
        prompt: str,
        context: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        """
        Generate a completion response based on the prompt and optional context using OpenAI.

        Args:
            prompt: The input prompt or question
            context: Optional context to inform the completion
            temperature: Controls randomness of output (0.0-1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Dictionary with completion text and metadata
        """
        system_prompt = "You are a helpful, accurate assistant."
        user_prompt = prompt

        if context:
            user_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

        response = self.client.chat.completions.create(
            model=self.completion_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return {
            "text": response.choices[0].message.content,
            "model": response.model,
            "token_usage": {
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
