"""
SmartByte Backend - Main Application

This is the entry point for the FastAPI application.
It configures the application, registers all routers, and sets up middleware.

To run the application:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

Or with Docker:
    docker compose up --build
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.database import init_db
from api.conversation import router as conversation_router
from api.admin import router as admin_router


# ==================== Application Lifespan ====================
# This runs once when the application starts and once when it shuts down

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Startup: Initialize database tables
    Shutdown: Clean up resources (if needed)
    """
    # ===== Startup =====
    print("🚀 Starting SmartByte Backend...")
    
    # Initialize database - creates tables if they don't exist
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise
    
    print("SmartByte Backend is ready!")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    
    yield  # Application runs here
    
    # ===== Shutdown =====
    print("Shutting down SmartByte Backend...")


# ==================== Create FastAPI Application ====================

app = FastAPI(
    title="SmartByte API",
    description="""
    ## SmartByte - AI-Powered Computer Store Sales Assistant
    
    SmartByte is an intelligent sales assistant that helps customers find 
    the perfect computer based on their needs, budget, and preferences.
    
    ### Features:
    - **Smart Recommendations**: AI-powered product matching based on customer profile
    - **Customer Type Detection**: Automatic identification of Student, Engineer, Gamer, or Other
    - **Upselling**: Intelligent accessory recommendations
    - **Guardrails**: Never invents products, prices, or specifications
    
    ### API Groups:
    - **Conversation API**: Customer-facing chat endpoints
    - **Admin API**: Administrative functions and analytics
    
    ### Authentication:
    Currently, the Admin API is not protected by authentication.
    In production, implement appropriate security measures.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc alternative
    openapi_url="/openapi.json"
)


# ==================== CORS Middleware ====================
# This allows the frontend (React) to communicate with the backend

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React development server
        "http://localhost:5173",      # Vite development server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"                           # Allow all in development (restrict in production!)
    ],
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)


# ==================== Register Routers ====================
# Each router handles a group of related endpoints

# Conversation API - Customer chat and recommendations
# Endpoints: POST /api/conversation/message
app.include_router(
    conversation_router,
    prefix="/api/conversation",
    tags=["Conversation"]
)

# Admin API - Management and analytics
# Endpoints:
#   GET  /api/admin/metrics
#   GET  /api/admin/sessions
#   GET  /api/admin/sessions/{session_id}
#   POST /api/admin/products/upload
app.include_router(
    admin_router,
    prefix="/api",
    tags=["Admin"]
)


# ==================== Root Endpoints ====================

@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Returns basic information about the API"
)
async def root():
    """
    Root endpoint - provides basic API information.
    
    This is useful for:
    - Verifying the API is running
    - Getting links to documentation
    - Quick reference for available endpoints
    """
    return {
        "name": "SmartByte API",
        "version": "1.0.0",
        "description": "AI-Powered Computer Store Sales Assistant",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "conversation": {
                "POST /api/conversation/message": "Process customer message and get recommendations"
            },
            "admin": {
                "GET /api/admin/metrics": "Get system analytics",
                "GET /api/admin/sessions": "List all sessions (with pagination)",
                "GET /api/admin/sessions/{session_id}": "Get session details",
                "POST /api/admin/products/upload": "Upload products from CSV"
            }
        }
    }


@app.get(
    "/health",
    tags=["Root"],
    summary="Health Check",
    description="Check if the API is healthy and running"
)
async def health_check():
    """
    Global health check endpoint.
    
    This is used by:
    - Load balancers to check if service is healthy
    - Monitoring systems
    - Docker health checks
    """
    return {
        "status": "healthy",
        "service": "smartbyte-api",
        "version": "1.0.0"
    }


# ==================== Error Handlers ====================
# These catch unhandled exceptions and return proper HTTP responses

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    This ensures that even if we miss an exception somewhere,
    the user gets a proper JSON response instead of an ugly error page.
    """
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "error_type": type(exc).__name__
        }
    )


# ==================== Run with Python directly ====================
# This allows running with: python -m backend.main

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )