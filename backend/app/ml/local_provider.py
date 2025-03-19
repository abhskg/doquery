"""Local model provider implementation using locally deployed models."""

import json
import os
from typing import Any, Dict, List

import numpy as np
import requests

from app.core.config import settings
from app.ml.base import ModelProvider


class LocalProvider(ModelProvider):
    """
    Local model provider implementation.

    This class provides an interface to locally deployed models.
    Assumes models are hosted using a REST API server like LLaMA.cpp server,
    text-embeddings-inference, or similar.
    """

    def __init__(self):
        """Initialize the local model provider."""
        self.server_url = settings.LOCAL_MODEL_SERVER_URL
        self.embedding_model_path = settings.LOCAL_EMBEDDING_MODEL_PATH
        self.completion_model_path = settings.LOCAL_COMPLETION_MODEL_PATH
        self.embedding_model = settings.LOCAL_EMBEDDING_MODEL
        self.completion_model = settings.LOCAL_COMPLETION_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a given text using local model.

        Args:
            text: The text to generate an embedding for

        Returns:
            A list of floats representing the embedding vector
        """
        try:
            # Call local embedding model API
            response = requests.post(
                f"{self.server_url}/embeddings",
                json={"input": text, "model": self.embedding_model},
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [{}])[0].get(
                    "embedding", [0.0] * self.dimension
                )
            else:
                # Fallback to a zero vector if API call fails
                print(f"Error generating embedding: {response.text}")
                return [0.0] * self.dimension
        except Exception as e:
            print(f"Exception in get_embedding: {str(e)}")
            return [0.0] * self.dimension

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using local model.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        try:
            # Call local embedding model API
            response = requests.post(
                f"{self.server_url}/embeddings",
                json={"input": texts, "model": self.embedding_model},
            )

            if response.status_code == 200:
                data = response.json()
                embeddings = [
                    item.get("embedding", [0.0] * self.dimension)
                    for item in data.get("data", [])
                ]

                # Ensure we have the right number of embeddings
                if len(embeddings) != len(texts):
                    # Fill in missing embeddings with zeros
                    embeddings = embeddings + [[0.0] * self.dimension] * (
                        len(texts) - len(embeddings)
                    )

                return embeddings
            else:
                # Fallback to zero vectors if API call fails
                print(f"Error generating embeddings: {response.text}")
                return [[0.0] * self.dimension for _ in texts]
        except Exception as e:
            print(f"Exception in get_embeddings: {str(e)}")
            return [[0.0] * self.dimension for _ in texts]

    def generate_completion(
        self,
        prompt: str,
        context: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        """
        Generate a completion response based on the prompt and optional context using local model.

        Args:
            prompt: The input prompt or question
            context: Optional context to inform the completion
            temperature: Controls randomness of output (0.0-1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Dictionary with completion text and metadata
        """
        try:
            system_prompt = "You are a helpful, accurate assistant."
            user_prompt = prompt

            if context:
                user_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

            # Call local completion model API
            response = requests.post(
                f"{self.server_url}/chat/completions",
                json={
                    "model": self.completion_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "text": data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", ""),
                    "model": self.completion_model,
                    "token_usage": data.get("usage", {}),
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
