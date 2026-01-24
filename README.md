# SmartByte

This repository contains a full-stack application for SmartByte:
- **Backend:** FastAPI (Python)
- **Frontend:** React + TypeScript (Vite)

## Quick start (local)
- Backend: `cd backend` → create venv → `pip install -r requirements.txt` → `uvicorn main:app --reload`
- Frontend: `cd frontend` → `npm install` → `npm run dev`

## Scalability Considerations

### Current Implementation (Development)

The current system is optimized for development and testing with approximately 30 products. Key design decisions that support future scaling:

**Database Optimizations:**
- Indexes on frequently queried columns (price, stock, category, session_id)
- Bulk insert operations for loading products from CSV
- Query filtering at database level (not in Python)
- SQLAlchemy ORM for database abstraction

**LLM Integration:**
- Pre-filtering products before sending to LLM
- Only in-stock products are considered
- Category and price filtering reduces context size

### Production Scaling (10,000+ Products)

When scaling to thousands of products and many concurrent users, the following changes would be required:

**1. Database Migration**
- **Switch from SQLite to PostgreSQL** (single line change in configuration)
  - SQLite is single-file and locks on concurrent writes
  - PostgreSQL handles thousands of concurrent connections
  - Better query optimization for large datasets

**2. API Enhancements**
- **Pagination**: Return products in pages (50-100 per page) instead of all at once
- **Connection pooling**: Reuse database connections instead of creating new ones
- **Rate limiting**: Prevent abuse and ensure fair resource distribution

**3. LLM Optimization**
- **Advanced filtering**: Use customer intent to narrow down products more aggressively
  - Example: "student" + "portable" → filter by weight, RAM requirements, price range
  - Goal: Send only 10-20 most relevant products to LLM (not 500)
- **Product scoring**: Rank products by relevance before sending to LLM
- **Caching**: Cache LLM responses for identical or similar queries

**4. Performance Improvements**
- **Redis caching**: Cache frequent queries (e.g., "cheapest laptops") for 5-10 minutes
- **Background tasks**: Process large CSV uploads asynchronously (Celery/FastAPI Background Tasks)
- **CDN**: Serve static content (if any) through Content Delivery Network
- **Load balancing**: Multiple backend instances behind a load balancer

**5. Monitoring and Maintenance**
- **Query performance monitoring**: Identify slow queries and optimize
- **Index optimization**: Add/remove indexes based on actual query patterns
- **Database vacuuming**: Regular maintenance for PostgreSQL
- **Error tracking**: Sentry or similar for production error monitoring

### Code Changes Required

Most of the scalability improvements require **zero code changes** thanks to the layered architecture:
- Database switch: Change one configuration variable
- Pagination: Add optional parameters to existing repository functions
- Caching: Decorator pattern on repository methods
- Background tasks: Wrap upload endpoint with FastAPI `BackgroundTasks`

## Future Enhancements

If the system grows significantly in complexity, the following tools could be integrated:

**LangChain/LangGraph**: For more complex conversation flows with multiple decision points and memory management.

**Hugging Face Models**: For running models locally without API costs, particularly useful for:
- Privacy-sensitive applications
- High-volume scenarios where API costs are prohibitive  
- Offline environments

**Current Implementation**: The current architecture uses direct OpenAI API calls, which provides:
- Simplicity and maintainability
- Easy debugging
- High-quality responses
- Lower development time

The modular design (LLM Provider pattern) allows easy integration of alternative LLM sources if needed in the future.
