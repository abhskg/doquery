"""Model provider factory."""

from app.core.config import settings
from app.ml.base import ModelProvider


def get_model_provider() -> ModelProvider:
    """
    Factory function to get the appropriate model provider based on settings.
    
    Returns:
        An instance of a ModelProvider implementation
    """
    provider_type = settings.MODEL_PROVIDER.lower()
    
    if provider_type == "openai":
        from app.ml.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider_type == "local":
        from app.ml.local_provider import LocalProvider
        return LocalProvider()
    elif provider_type == "huggingface":
        from app.ml.huggingface_provider import HuggingFaceProvider
        return HuggingFaceProvider()
    else:
        # Default to OpenAI if the provider type is not recognized
        from app.ml.openai_provider import OpenAIProvider
        print(f"Warning: Unrecognized model provider '{provider_type}'. Defaulting to OpenAI.")
        return OpenAIProvider() 