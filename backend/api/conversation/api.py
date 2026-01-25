"""
Conversation API Endpoints

Handles customer conversations and product recommendations.

This module contains the main conversation endpoint that:
1. Receives user messages
2. Identifies customer type
3. Matches products to customer needs
4. Generates AI-powered recommendations
5. Selects upsell products
6. Returns structured response
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from db.database import get_db
from services.conversation import RecommendationService
from services.conversation.exceptions import (
    RecommendationError,
    ServiceError
)
from .schemas import ConversationMessageRequest, ConversationMessageResponse, ProductItem
from .exceptions import (
    MessageProcessingException,
    LLMServiceException,
    InvalidSessionException
)

# Create router for conversation endpoints
# This router will be registered in main.py with prefix "/api/conversation"
router = APIRouter(
    tags=["Conversation"],
    responses={
        500: {"description": "Internal server error"},
        503: {"description": "AI service unavailable"}
    }
)


@router.post(
    "/message",
    response_model=ConversationMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a conversation message",
    description="""
    Process a user message and return AI-powered product recommendations.
    
    **Workflow:**
    1. Receive user message and session ID
    2. Identify customer type (Student, Engineer, Gamer, Other) from conversation
    3. Filter products based on customer needs, budget, and stock availability
    4. Generate personalized recommendation using LLM
    5. Select relevant accessory for upselling
    6. Save conversation and recommendation to database
    
    **Guardrails:**
    - Only recommends products actually in stock
    - Only mentions real prices from database
    - Redirects off-topic conversations back to products
    - Never invents product specifications
    
    **Notes:**
    - Session is created automatically if it doesn't exist
    - Customer type is identified progressively through conversation
    - Recommendations are saved for analytics
    """
)
async def process_message(
    request: ConversationMessageRequest,
    db: Session = Depends(get_db)
) -> ConversationMessageResponse:
    """
    Main endpoint for processing conversation messages.
    
    This is the heart of the customer-facing API. When a user sends a message,
    this endpoint orchestrates all the services to generate a response.
    
    Args:
        request: The conversation message request containing session_id and message
        db: Database session (injected by FastAPI)
    
    Returns:
        ConversationMessageResponse with assistant message, customer type,
        recommended products, and optional upsell item
    
    Raises:
        InvalidSessionException: If session_id is invalid (400)
        LLMServiceException: If LLM service fails (503)
        MessageProcessingException: If processing fails (500)
    
    Example Request:
        POST /api/conversation/message
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "message": "I'm a student looking for a laptop, budget 3000 ILS"
        }
    
    Example Response:
        {
            "assistant_message": "Perfect! For student use, I recommend...",
            "customer_type": "Student",
            "recommended_items": [{...}],
            "upsell_item": {...}
        }
    """
    
    try:
        # Step 1: Validate session_id format (basic validation)
        # The request model already validated that it's not empty, but we can
        # add additional validation here if needed (e.g., UUID format)
        if not request.session_id or len(request.session_id.strip()) == 0:
            raise InvalidSessionException("Session ID cannot be empty")
        
        # Step 2: Initialize RecommendationService
        # This service orchestrates all business logic:
        # - Customer identification
        # - Product matching
        # - LLM interaction
        # - Upsell selection
        # - Database operations
        try:
            recommendation_service = RecommendationService(db)
        except Exception as e:
            # If service initialization fails, it's likely an LLM configuration issue
            raise LLMServiceException(
                f"Failed to initialize AI service: {str(e)}"
            )
        
        # Step 3: Process the message through the recommendation service
        # This is where all the magic happens:
        # - Conversation history is retrieved
        # - Customer type is identified or updated
        # - Products are filtered based on needs
        # - LLM generates personalized response
        # - Everything is saved to database
        try:
            result = recommendation_service.process_message(
                session_id=request.session_id,
                user_message=request.message
            )
        except RecommendationError as e:
            # RecommendationError is our custom exception from the service layer
            # It means something went wrong in the business logic
            raise MessageProcessingException(
                f"Failed to generate recommendation: {str(e)}"
            )
        except ServiceError as e:
            # ServiceError is the base exception for all service-layer errors
            raise MessageProcessingException(
                f"Service error: {str(e)}"
            )
        
        # Step 4: Transform the result into the response format
        # The service returns a dict, we need to convert it to our Pydantic model
        # This ensures the response matches our schema exactly
        
        # Convert recommended items to ProductItem schema
        recommended_items = []
        for item_dict in result.get("recommended_items", []):
            # ProductItem.from_attributes will convert the dict to our schema
            recommended_items.append(ProductItem(**item_dict))
        
        # Convert upsell item if present
        upsell_item = None
        if result.get("upsell_item"):
            upsell_item = ProductItem(**result["upsell_item"])
        
        # Step 5: Build and return the response
        response = ConversationMessageResponse(
            assistant_message=result["assistant_message"],
            customer_type=result["customer_type"],
            recommended_items=recommended_items,
            upsell_item=upsell_item
        )
        
        return response
    
    except InvalidSessionException:
        # Re-raise our custom exceptions as-is
        # FastAPI will convert these to HTTP responses automatically
        raise
    
    except LLMServiceException:
        # Re-raise LLM service exceptions
        raise
    
    except MessageProcessingException:
        # Re-raise processing exceptions
        raise
    
    except HTTPException:
        # Re-raise any HTTPExceptions (including our custom ones)
        raise
    
    except Exception as e:
        # Catch any unexpected errors and convert to 500 Internal Server Error
        # In production, we would log this error for debugging
        print(f"Unexpected error in conversation endpoint: {str(e)}")
        raise MessageProcessingException(
            "An unexpected error occurred while processing your message. "
            "Please try again or contact support if the problem persists."
        )


# Health check endpoint - useful for monitoring
@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the conversation API is operational"
)
async def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint.
    
    This is useful for:
    - Load balancers to check if service is up
    - Monitoring systems to track uptime
    - Quick debugging to see if API is responsive
    
    Returns:
        Simple JSON with status
    """
    return {
        "status": "healthy",
        "service": "conversation-api"
    }