"""
Conversation API Exceptions

Custom exceptions for the conversation API with HTTP status codes.
These exceptions are caught by FastAPI and converted to proper HTTP responses.
"""

from fastapi import HTTPException, status


class ConversationAPIException(HTTPException):
    """
    Base exception for all conversation API errors.
    
    This inherits from FastAPI's HTTPException, which means when we raise
    one of these exceptions, FastAPI automatically converts it to an HTTP
    response with the right status code and error message.
    """
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class InvalidSessionException(ConversationAPIException):
    """
    Raised when session_id is invalid or cannot be processed.
    
    HTTP Status: 400 Bad Request
    """
    def __init__(self, detail: str = "Invalid session ID"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class MessageProcessingException(ConversationAPIException):
    """
    Raised when message processing fails.
    
    This could happen if:
    - LLM service is unavailable
    - Database operation fails
    - Unexpected error in business logic
    
    HTTP Status: 500 Internal Server Error
    """
    def __init__(self, detail: str = "Failed to process message"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LLMServiceException(ConversationAPIException):
    """
    Raised when LLM service fails.
    
    This is a specific type of processing error for LLM-related issues.
    
    HTTP Status: 503 Service Unavailable
    """
    def __init__(self, detail: str = "AI service temporarily unavailable"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)