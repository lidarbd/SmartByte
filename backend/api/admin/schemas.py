"""
Admin API Schemas

These schemas define the structure of requests and responses for admin endpoints.
Includes metrics, session management, and CSV upload functionality.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== Metrics Schemas ====================

class DailyConsultation(BaseModel):
    """Single data point for daily consultations chart"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    count: int = Field(..., description="Number of consultations on this date")


class TopProduct(BaseModel):
    """Single product in top recommended products"""
    product_name: str = Field(..., description="Product name")
    brand: str = Field(..., description="Product brand")
    recommendation_count: int = Field(..., description="Times this product was recommended")


class CustomerSegment(BaseModel):
    """Single segment in customer segmentation"""
    customer_type: str = Field(..., description="Student, Engineer, Gamer, or Other")
    count: int = Field(..., description="Number of customers of this type")
    percentage: float = Field(..., description="Percentage of total customers")


class MetricsResponse(BaseModel):
    """
    Response schema for GET /api/admin/metrics

    Provides analytics data for the admin dashboard.

    Example:
        {
            "daily_consultations": [
                {"date": "2025-01-20", "count": 15},
                {"date": "2025-01-21", "count": 23},
                ...
            ],
            "top_recommended_products": [
                {
                    "product_name": "ThinkPad E14",
                    "brand": "Lenovo",
                    "recommendation_count": 45
                },
                ...
            ],
            "customer_segmentation": [
                {
                    "customer_type": "Student",
                    "count": 120,
                    "percentage": 45.5
                },
                ...
            ]
        }
    """
    daily_consultations: List[DailyConsultation] = Field(
        default=[],
        description="Consultation counts by day for the last 30 days"
    )

    top_recommended_products: List[TopProduct] = Field(
        default=[],
        description="Top 10 most recommended products"
    )

    customer_segmentation: List[CustomerSegment] = Field(
        default=[],
        description="Distribution of customers by type"
    )


# ==================== Sessions Schemas ====================

class SessionSummary(BaseModel):
    """
    Summary of a single chat session for the sessions list.
    
    This is a lightweight version - doesn't include full conversation,
    just the key info for displaying in a table.
    """
    session_id: str = Field(..., description="External session ID")
    customer_type: Optional[str] = Field(None, description="Identified customer type")
    started_at: datetime = Field(..., description="When the session started")
    ended_at: Optional[datetime] = Field(None, description="When the session ended")
    message_count: int = Field(..., description="Number of messages in conversation")
    recommendation_count: int = Field(..., description="Number of products recommended")
    
    class Config:
        from_attributes = True


class SessionsListResponse(BaseModel):
    """
    Response schema for GET /api/admin/sessions
    
    Includes pagination information.
    
    Example:
        {
            "sessions": [...],
            "total": 150,
            "page": 1,
            "page_size": 20,
            "total_pages": 8
        }
    """
    sessions: List[SessionSummary] = Field(..., description="List of sessions")
    total: int = Field(..., description="Total number of sessions")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class ChatMessageDetail(BaseModel):
    """A single message in a conversation"""
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When the message was sent")
    
    class Config:
        from_attributes = True


class RecommendationDetail(BaseModel):
    """Details of a single recommendation made in the session"""
    product_id: int = Field(..., description="Recommended product ID")
    product_name: str = Field(..., description="Product name")
    product_price: float = Field(..., description="Product price")
    upsell_product_id: Optional[int] = Field(None, description="Upsell product ID if any")
    upsell_product_name: Optional[str] = Field(None, description="Upsell product name")
    recommendation_text: str = Field(..., description="Full recommendation text")
    timestamp: datetime = Field(..., description="When recommendation was made")


class SessionDetailResponse(BaseModel):
    """
    Response schema for GET /api/admin/sessions/{session_id}
    
    Provides complete session details including full conversation
    and all recommendations.
    
    Example:
        {
            "session_id": "abc-123",
            "customer_type": "Student",
            "started_at": "2025-01-24T10:00:00",
            "ended_at": null,
            "messages": [
                {
                    "role": "user",
                    "content": "I need a laptop",
                    "timestamp": "2025-01-24T10:00:00"
                },
                {
                    "role": "assistant",
                    "content": "I'd be happy to help...",
                    "timestamp": "2025-01-24T10:00:05"
                }
            ],
            "recommendations": [
                {
                    "product_id": 1,
                    "product_name": "ThinkPad E14",
                    "product_price": 3890,
                    ...
                }
            ]
        }
    """
    session_id: str = Field(..., description="External session ID")
    customer_type: Optional[str] = Field(None, description="Identified customer type")
    started_at: datetime = Field(..., description="Session start time")
    ended_at: Optional[datetime] = Field(None, description="Session end time")
    messages: List[ChatMessageDetail] = Field(default=[], description="Full conversation")
    recommendations: List[RecommendationDetail] = Field(default=[], description="All recommendations made")


# ==================== Authentication Schemas ====================

class LoginRequest(BaseModel):
    """
    Request schema for POST /api/admin/login

    Example:
        {
            "password": "admin123"
        }
    """
    password: str = Field(..., description="Admin password")


class LoginResponse(BaseModel):
    """
    Response schema for POST /api/admin/login

    Returns authentication token and expiration time.

    Example:
        {
            "token": "abc123...",
            "expires_at": "2025-01-28T10:00:00Z"
        }
    """
    token: str = Field(..., description="Authentication token")
    expires_at: str = Field(..., description="Token expiration timestamp (ISO format)")


# ==================== CSV Upload Schemas ====================

class CSVUploadResponse(BaseModel):
    """
    Response schema for POST /api/admin/products/upload
    
    Provides statistics about the CSV upload operation.
    
    Example:
        {
            "message": "CSV processed successfully",
            "statistics": {
                "total_rows": 30,
                "loaded": 28,
                "updated": 2,
                "skipped": 0,
                "errors": []
            }
        }
    """
    message: str = Field(..., description="Success or error message")
    statistics: Dict[str, Any] = Field(
        ...,
        description="Upload statistics (total_rows, loaded, updated, skipped, errors)"
    )