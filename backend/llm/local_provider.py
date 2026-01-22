"""
Local LLM Provider Implementation (Stub)

This is a placeholder for local models (Ollama, LLaMA, etc.).
For now, it's just a stub that returns dummy responses.

To implement a real local provider:
1. Install Ollama or use HuggingFace transformers
2. Replace the stub implementation with actual model calls
3. Update config to allow switching between providers
"""

from typing import List, Dict, Optional
from .base import LLMProvider, LLMProviderError


class LocalProvider(LLMProvider):
    """
    Local LLM provider - currently a stub.
    
    This is a placeholder for future implementation of local models.
    For the assignment, OpenAI provider is sufficient.
    """
    
    def __init__(self, model_name: str = "llama2"):
        """
        Initialize local provider.
        
        Args:
            model_name: Name of local model to use
        """
        self.model_name = model_name
        print(f"LocalProvider is a stub. Using dummy responses.")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Stub implementation - returns dummy response.
        
        TODO: Implement actual local model inference here.
        """
        return self._get_dummy_response(prompt)
    
    def generate_with_context(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Stub implementation - returns dummy response.
        
        TODO: Implement actual local model inference with context.
        """
        # Get the last user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        last_message = user_messages[-1]["content"] if user_messages else "Hello"
        
        return self._get_dummy_response(last_message)
    
    def _get_dummy_response(self, prompt: str) -> str:
        """
        Generate a dummy response for testing.
        
        This is useful during development when you don't want to spend
        money on API calls, or when testing without internet connection.
        """
        prompt_lower = prompt.lower()
        
        if "laptop" in prompt_lower or "computer" in prompt_lower:
            return """Based on your needs, I recommend the Lenovo ThinkPad E14 Gen 4.

This laptop offers:
- Intel i5 processor for smooth performance
- 16GB RAM for multitasking
- 512GB SSD for fast storage
- Windows 11 Pro
- Price: 3,890 ILS

For accessories, I suggest adding a wireless mouse for better productivity."""
        
        elif "student" in prompt_lower:
            return """For a student, I recommend focusing on:
- Portability (lightweight laptop)
- Good battery life
- Sufficient performance for Office and browsing
- Affordable price point

The Lenovo IdeaPad 3 would be a great choice at 2,790 ILS."""
        
        elif "gaming" in prompt_lower or "gamer" in prompt_lower:
            return """For gaming, you'll need:
- Dedicated GPU (RTX 3060 or better)
- At least 16GB RAM
- Fast processor
- Good cooling system

I recommend the Dell G15 5520 with RTX 3060 graphics."""
        
        else:
            return """Thank you for your message. I'm here to help you find the perfect computer.

Could you tell me more about:
- What will you use the computer for?
- What's your budget?
- Do you prefer laptop or desktop?

This will help me provide better recommendations."""