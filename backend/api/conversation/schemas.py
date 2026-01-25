"""
Conversation API Schemas

These schemas define the structure of requests and responses for the conversation API.
Pydantic validates all data automatically and provides clear error messages.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ConversationMessageRequest(BaseModel):
    """
    Request schema for POST /api/conversation/message
    
    This defines what the client must send when starting or continuing a conversation.
    
    Example:
        {
            "session_id": "abc-123-def-456",
            "message": "I need a laptop for university"
        }
    """
    session_id: str = Field(
        ...,
        description="Unique session identifier (UUID recommended)",
        min_length=1,
        max_length=100,
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    message: str = Field(
        ...,
        description="User's message",
        min_length=1,
        max_length=2000,
        example="I need a laptop for university, budget around 3000 ILS"
    )
    
    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v):
        """Ensure message is not just whitespace"""
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
    
    @field_validator('session_id')
    @classmethod
    def session_id_not_empty(cls, v):
        """Ensure session_id is not just whitespace"""
        if not v.strip():
            raise ValueError('Session ID cannot be empty')
        return v.strip()


class ProductItem(BaseModel):
    """
    Schema for a single product in the response.
    
    This represents one product that we're recommending to the customer.
    """
    id: int = Field(..., description="Product database ID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    brand: str = Field(..., description="Product brand")
    product_type: str = Field(..., description="laptop, desktop, or accessory")
    category: str = Field(..., description="Product category")
    price: float = Field(..., description="Price in ILS")
    stock: int = Field(..., description="Available stock")
    specs: Optional[Dict[str, Any]] = Field(None, description="Technical specifications")
    description: Optional[str] = Field(None, description="Product description")
    
    class Config:
        # This tells Pydantic how to convert a SQLAlchemy model to this schema
        from_attributes = True


class ConversationMessageResponse(BaseModel):
    """
    Response schema for POST /api/conversation/message
    
    This defines what the API returns after processing the user's message.
    It matches the exact format specified in the assignment.
    
    Example:
        {
            "assistant_message": "Based on your needs as a student...",
            "customer_type": "Student",
            "recommended_items": [
                {
                    "id": 1,
                    "sku": "LAP-001",
                    "name": "ThinkPad E14",
                    ...
                }
            ],
            "upsell_item": {
                "id": 15,
                "sku": "ACC-001",
                "name": "Wireless Mouse",
                ...
            }
        }
    """
    assistant_message: str = Field(
        ...,
        description="AI assistant's response to the user"
    )
    
    customer_type: str = Field(
        ...,
        description="Identified customer type: Student, Engineer, Gamer, or Other"
    )
    
    recommended_items: List[ProductItem] = Field(
        default=[],
        description="List of recommended products (usually 1, can be 0 if no match)"
    )
    
    upsell_item: Optional[ProductItem] = Field(
        None,
        description="Optional accessory for upselling"
    )