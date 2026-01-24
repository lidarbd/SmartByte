"""
LLM Provider Package

This package provides a unified interface for interacting with different LLM providers.

Usage:
    from backend.llm import get_llm_provider
    
    provider = get_llm_provider()  # Automatically selects based on config
    response = provider.generate("Recommend a laptop for gaming")
"""

from .base import LLMProvider, LLMProviderError
from .openai_provider import OpenAIProvider
from .local_provider import LocalProvider
from core.config import settings


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider based on configuration.
    
    Returns:
        LLMProvider instance (OpenAI or Local)
    
    Raises:
        ValueError: If provider type is not recognized
        LLMProviderError: If provider initialization fails
    
    Example:
        # In your service layer:
        provider = get_llm_provider()
        response = provider.generate("Hello")
    """
    provider_type = settings.LLM_PROVIDER.lower()
    
    if provider_type == "openai":
        if not settings.OPENAI_API_KEY:
            raise LLMProviderError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4"  # Can be made configurable via settings
        )
    
    elif provider_type == "local":
        return LocalProvider()
    
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_type}. "
            f"Supported providers: 'openai', 'local'"
        )


# Export commonly used items
__all__ = [
    'LLMProvider',
    'LLMProviderError',
    'OpenAIProvider',
    'LocalProvider',
    'get_llm_provider'
]