"""
OpenAI Provider Implementation

This module implements the LLM provider interface for OpenAI's GPT models.
It handles API calls, error handling, and response parsing.
"""

from typing import List, Dict, Optional
from openai import OpenAI
from openai import OpenAIError
from .base import LLMProvider, LLMProviderError


class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT provider implementation.
    
    This class handles all communication with OpenAI's API.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
                   Options: gpt-4, gpt-4-turbo, gpt-3.5-turbo
        """
        if not api_key:
            raise LLMProviderError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using OpenAI's chat completion API.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: 0.0-1.0, controls randomness
            max_tokens: Maximum response length
        
        Returns:
            Generated text
        
        Example:
            provider = OpenAIProvider(api_key="sk-...")
            response = provider.generate(
                prompt="Recommend a laptop for a student",
                system_prompt="You are a computer store sales assistant"
            )
        """
        try:
            # Build messages array
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add user prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract and return the text
            return response.choices[0].message.content
        
        except OpenAIError as e:
            # Wrap OpenAI errors in our custom exception
            raise LLMProviderError(f"OpenAI API error: {str(e)}")
        
        except Exception as e:
            # Catch any other unexpected errors
            raise LLMProviderError(f"Unexpected error calling OpenAI: {str(e)}")
    
    def generate_with_context(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text with full conversation context.
        
        Args:
            messages: Conversation history
            temperature: Creativity level
            max_tokens: Maximum response length
        
        Returns:
            Generated text
        
        Example:
            messages = [
                {"role": "system", "content": "You are a sales assistant"},
                {"role": "user", "content": "I need a laptop"},
                {"role": "assistant", "content": "What's your budget?"},
                {"role": "user", "content": "Around 5000 ILS"}
            ]
            response = provider.generate_with_context(messages)
        """
        try:
            # Call OpenAI API with full context
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except OpenAIError as e:
            raise LLMProviderError(f"OpenAI API error: {str(e)}")
        
        except Exception as e:
            raise LLMProviderError(f"Unexpected error calling OpenAI: {str(e)}")