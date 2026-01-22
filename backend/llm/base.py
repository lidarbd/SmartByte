"""
Base LLM Provider Interface

This module defines the abstract base class that all LLM providers must implement.
This allows us to easily switch between OpenAI, Claude, local models, etc.
without changing any business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Any LLM provider (OpenAI, Claude, Gemini, local model) must implement this interface.
    This ensures consistent behavior regardless of which LLM we're using.
    """
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions for the LLM
            temperature: Creativity level (0.0 = deterministic, 1.0 = very creative)
            max_tokens: Maximum length of response
        
        Returns:
            Generated text response
        
        Raises:
            LLMProviderError: If the LLM call fails
        """
        pass
    
    @abstractmethod
    def generate_with_context(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text based on a conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [
                         {"role": "system", "content": "You are a helpful assistant"},
                         {"role": "user", "content": "Hello!"},
                         {"role": "assistant", "content": "Hi! How can I help?"},
                         {"role": "user", "content": "I need a laptop"}
                     ]
            temperature: Creativity level
            max_tokens: Maximum length of response
        
        Returns:
            Generated text response
        
        Raises:
            LLMProviderError: If the LLM call fails
        """
        pass


class LLMProviderError(Exception):
    """
    Custom exception for LLM provider errors.
    
    Use this to wrap any errors from the LLM API so we can handle them
    consistently regardless of which provider is being used.
    """
    pass