"""HuggingFace model provider implementation using HuggingFace API."""

import requests
from typing import List, Dict, Any

from app.core.config import settings
from app.ml.base import ModelProvider


class HuggingFaceProvider(ModelProvider):
    """
    HuggingFace model provider implementation.

    This class provides an interface to the HuggingFace API for
    embeddings and completions.
    """

    def __init__(self):
        """Initialize the HuggingFace provider."""
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.embedding_model = settings.HUGGINGFACE_EMBEDDING_MODEL
        self.completion_model = settings.HUGGINGFACE_COMPLETION_MODEL
        self.api_url = "https://api-inference.huggingface.co/models"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.dimension = settings.EMBEDDING_DIMENSION

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a given text using HuggingFace.

        Args:
            text: The text to generate an embedding for

        Returns:
            A list of floats representing the embedding vector
        """
        try:
            # Call HuggingFace embedding API
            response = requests.post(
                f"{self.api_url}/{self.embedding_model}",
                headers=self.headers,
                json={"inputs": text},
            )

            if response.status_code == 200:
                # Extract embeddings from response
                embedding = response.json()

                # Handle different response formats
                if isinstance(embedding, list) and len(embedding) > 0:
                    if isinstance(embedding[0], list):
                        # Some models return a list of sentence embeddings
                        return embedding[0]
                    else:
                        # Some models return a single embedding vector
                        return embedding

                # Fallback for unexpected response format
                print(f"Unexpected embedding format: {embedding}")
                return [0.0] * self.dimension
            else:
                # Fallback to a zero vector if API call fails
                print(f"Error generating embedding: {response.text}")
                return [0.0] * self.dimension
        except Exception as e:
            print(f"Exception in get_embedding: {str(e)}")
            return [0.0] * self.dimension

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using HuggingFace.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        # For simplicity, we'll process each text individually
        return [self.get_embedding(text) for text in texts]

    def generate_completion(
        self,
        prompt: str,
        context: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        """
        Generate a completion response based on the prompt and optional context using HuggingFace.

        Args:
            prompt: The input prompt or question
            context: Optional context to inform the completion
            temperature: Controls randomness of output (0.0-1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Dictionary with completion text and metadata
        """
        try:
            user_prompt = prompt

            if context:
                user_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

            # Prepare the payload for the model
            payload = {
                "inputs": user_prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    "return_full_text": False,
                },
            }

            # Call HuggingFace completion API
            response = requests.post(
                f"{self.api_url}/{self.completion_model}",
                headers=self.headers,
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()

                # Handle different response formats
                completion_text = ""
                if isinstance(data, list) and len(data) > 0:
                    if "generated_text" in data[0]:
                        completion_text = data[0]["generated_text"]
                    else:
                        completion_text = data[0]
                elif isinstance(data, dict) and "generated_text" in data:
                    completion_text = data["generated_text"]
                else:
                    completion_text = str(data)

                return {
                    "text": completion_text,
                    "model": self.completion_model,
                    "token_usage": {},  # HuggingFace doesn't provide token usage stats
                }
            else:
                # Return error message if API call fails
                error_msg = f"Error: {response.text}"
                print(error_msg)
                return {
                    "text": f"Sorry, I couldn't process your request due to a technical issue. {error_msg}",
                    "model": self.completion_model,
                    "token_usage": {},
                }
        except Exception as e:
            error = str(e)
            print(f"Exception in generate_completion: {error}")
            return {
                "text": f"Sorry, I couldn't process your request due to a technical issue. {error}",
                "model": self.completion_model,
                "token_usage": {},
            }
