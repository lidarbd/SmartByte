"""
Admin API Endpoints
"""

import math
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta

from db.database import get_db
from db.conversation.models import (
    ChatSession,
    ChatMessage,
    Recommendation,
    Product
)
from services.conversation import CSVLoader
from services.conversation.exceptions import CSVParsingError

from .schemas import (
    MetricsResponse,
    DailyConsultation,
    TopProduct,
    CustomerSegment,
    SessionsListResponse,
    SessionSummary,
    SessionDetailResponse,
    ChatMessageDetail,
    RecommendationDetail,
    CSVUploadResponse
)

# Create router
router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={500: {"description": "Internal server error"}}
)


# ==================== GET /api/admin/metrics ====================

@router.get(
    "/metrics",
    response_model=MetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get system metrics and analytics"
)
async def get_metrics(db: Session = Depends(get_db)) -> MetricsResponse:
    """Calculate and return system metrics."""
    
    try:
        # Daily Consultations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        daily_query = (
            db.query(
                func.date(ChatSession.started_at).label('date'),
                func.count(ChatSession.id).label('count')
            )
            .filter(ChatSession.started_at >= thirty_days_ago)
            .group_by(func.date(ChatSession.started_at))
            .order_by(func.date(ChatSession.started_at))
            .all()
        )
        
        daily_consultations = [
            DailyConsultation(date=str(row.date), count=row.count)
            for row in daily_query
        ]
        
        # Top Recommended Products
        top_products_query = (
            db.query(
                Product.name.label('product_name'),
                Product.brand.label('brand'),
                func.count(Recommendation.id).label('recommendation_count')
            )
            .join(Recommendation, Recommendation.product_id == Product.id)
            .group_by(Product.id, Product.name, Product.brand)
            .order_by(desc(func.count(Recommendation.id)))
            .limit(10)
            .all()
        )
        
        top_recommended_products = [
            TopProduct(
                product_name=row.product_name,
                brand=row.brand,
                recommendation_count=row.recommendation_count
            )
            for row in top_products_query
        ]
        
        # Customer Segmentation
        segmentation_query = (
            db.query(
                ChatSession.customer_type.label('customer_type'),
                func.count(ChatSession.id).label('count')
            )
            .filter(ChatSession.customer_type.isnot(None))
            .group_by(ChatSession.customer_type)
            .all()
        )
        
        total_customers = sum(row.count for row in segmentation_query)
        
        customer_segmentation = [
            CustomerSegment(
                customer_type=row.customer_type,
                count=row.count,
                percentage=round((row.count / total_customers * 100), 2) if total_customers > 0 else 0
            )
            for row in segmentation_query
        ]
        
        return MetricsResponse(
            daily_consultations=daily_consultations,
            top_recommended_products=top_recommended_products,
            customer_segmentation=customer_segmentation
        )
    
    except Exception as e:
        print(f"Error in get_metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


# ==================== GET /api/admin/sessions ====================

@router.get(
    "/sessions",
    response_model=SessionsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all conversation sessions"
)
async def get_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    db: Session = Depends(get_db)
) -> SessionsListResponse:
    """List conversation sessions with pagination and search."""
    
    try:
        # Build query
        query = db.query(ChatSession)
        
        # Apply search filter
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (ChatSession.session_id.ilike(search_term)) |
                (ChatSession.customer_type.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        sessions = (
            query
            .order_by(desc(ChatSession.started_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        # Build summaries
        session_summaries = []
        for session in sessions:
            message_count = (
                db.query(func.count(ChatMessage.id))
                .filter(ChatMessage.session_id == session.id)
                .scalar()
            )
            
            recommendation_count = (
                db.query(func.count(Recommendation.id))
                .filter(Recommendation.session_id == session.id)
                .scalar()
            )
            
            session_summaries.append(
                SessionSummary(
                    session_id=session.session_id,
                    customer_type=session.customer_type,
                    started_at=session.started_at,
                    ended_at=session.ended_at,
                    message_count=message_count,
                    recommendation_count=recommendation_count
                )
            )
        
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        
        return SessionsListResponse(
            sessions=session_summaries,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    except Exception as e:
        print(f"Error in get_sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )


# ==================== GET /api/admin/sessions/{session_id} ====================

@router.get(
    "/sessions/{session_id}",
    response_model=SessionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed session information"
)
async def get_session_detail(
    session_id: str,
    db: Session = Depends(get_db)
) -> SessionDetailResponse:
    """Get complete details for a specific session."""
    
    try:
        # Find session
        session = (
            db.query(ChatSession)
            .filter(ChatSession.session_id == session_id)
            .first()
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID '{session_id}' not found"
            )
        
        # Load messages
        messages_query = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.timestamp)
            .all()
        )
        
        messages = [
            ChatMessageDetail(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            )
            for msg in messages_query
        ]
        
        # Load recommendations
        recommendations_query = (
            db.query(
                Recommendation,
                Product.name.label('product_name'),
                Product.price.label('product_price')
            )
            .join(Product, Recommendation.product_id == Product.id)
            .filter(Recommendation.session_id == session.id)
            .all()
        )
        
        recommendations = []
        for rec, product_name, product_price in recommendations_query:
            upsell_name = None
            if rec.upsell_product_id:
                upsell_product = (
                    db.query(Product)
                    .filter(Product.id == rec.upsell_product_id)
                    .first()
                )
                if upsell_product:
                    upsell_name = upsell_product.name
            
            recommendations.append(
                RecommendationDetail(
                    product_id=rec.product_id,
                    product_name=product_name,
                    product_price=product_price,
                    upsell_product_id=rec.upsell_product_id,
                    upsell_product_name=upsell_name,
                    recommendation_text=rec.recommendation_text,
                    timestamp=rec.created_at
                )
            )
        
        return SessionDetailResponse(
            session_id=session.session_id,
            customer_type=session.customer_type,
            started_at=session.started_at,
            ended_at=session.ended_at,
            messages=messages,
            recommendations=recommendations
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_session_detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session details: {str(e)}"
        )


# ==================== POST /api/admin/products/upload ====================

@router.post(
    "/products/upload",
    response_model=CSVUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload products from CSV file"
)
async def upload_products(
    file: UploadFile = File(..., description="CSV file"),
    db: Session = Depends(get_db)
) -> CSVUploadResponse:
    """Handle CSV file upload and product import."""
    
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file (.csv extension)"
            )
        
        # Read file content
        try:
            content = await file.read()
            content_str = content.decode('utf-8')
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read file: {str(e)}"
            )
        
        # Process CSV
        try:
            loader = CSVLoader(db)
            stats = loader.load_from_upload(
                file_content=content_str,
                upsert=True
            )
        except CSVParsingError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CSV format: {str(e)}"
            )
        
        # Build response
        if stats['loaded'] == 0 and stats.get('updated', 0) == 0:
            message = "No products were loaded. Check the errors list."
        elif len(stats.get('errors', [])) == 0:
            message = "CSV processed successfully with no errors"
        else:
            message = f"CSV processed with {len(stats['errors'])} errors"
        
        return CSVUploadResponse(
            message=message,
            statistics=stats
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload_products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV upload: {str(e)}"
        )


# Health check
@router.get("/health", status_code=status.HTTP_200_OK, summary="Health check")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "admin-api"}