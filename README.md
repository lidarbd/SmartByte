# SmartByte - AI-Powered Computer Recommendation System

SmartByte is an intelligent chatbot that helps customers find the perfect computer by analyzing their needs and recommending products from your inventory.

## 🎯 Key Features

- **Intelligent Recommendations**: AI-powered product matching based on customer type (Student, Engineer, Gamer, Business)
- **Natural Language Chat**: Hebrew conversational interface
- **Admin Dashboard**: Real-time metrics, session history, and product management
- **CSV Product Import**: Bulk upload and manage product catalog
- **Type-Safe Frontend**: React + TypeScript with comprehensive type definitions
- **Production-Ready Backend**: FastAPI with SQLAlchemy ORM

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.11+ and Node.js 18+ for local development

### Running the Application

```bash
# Clone the repository
git clone <repository-url>
cd smartbyte

# Start all services
docker compose up --build
```

**Access the application:**
- **Frontend (Chat)**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./smartbyte.db  # Development (default)
# DATABASE_URL=postgresql://user:password@localhost/smartbyte  # Production

# LLM Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o  # Options: gpt-4o, gpt-4-turbo, gpt-3.5-turbo

# Admin Configuration
ADMIN_PASSWORD=admin123 

```

#### SQLite Database

```python
DATABASE_URL = "sqlite:///./smartbyte.db"
```

### Choosing Your LLM

#### OpenAI (Default)
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```
- Best quality responses
- Easy integration
- Pay-per-use pricing

#### Alternative LLMs (Future Support)
The modular `LLMProvider` pattern allows easy integration of:
- Anthropic Claude
- Google Gemini
- Local Hugging Face models
- Azure OpenAI

---

## 🔐 Admin Dashboard Access

### 1. Navigate to Admin Login

```
http://localhost:5173/admin/login
```

### 2. Login Credentials

```
Password: admin123  (change in production!)
```

### 3. Dashboard Features

Once logged in, you can:
- 📊 View system metrics (sessions, recommendations, conversion rate)
- 📈 Analyze daily consultations and customer segmentation
- 🔍 Search and filter conversation sessions
- 📤 Upload products from CSV files
- 📋 View detailed session history

---

## 📊 Scalability Considerations

### Current Implementation (Development)

**Designed for:** ~30 products, single user  
**Database:** SQLite (single file)  
**Performance:** Optimized for rapid development

**Key Design Decisions Supporting Future Scaling:**
- ✅ Database indexes on frequently queried columns
- ✅ Bulk insert operations for CSV loading
- ✅ Query filtering at database level (not in Python)
- ✅ SQLAlchemy ORM for easy database migration
- ✅ Pre-filtering products before sending to LLM
- ✅ Modular architecture with separation of concerns

---

### Production Scaling (10,000+ Products)

**Target:** 10,000+ products, 1,000+ concurrent users

#### 1. Database Migration 🗄️

**Switch to PostgreSQL:**

```python
# Single line change
DATABASE_URL = "postgresql://user:password@localhost:5432/smartbyte"
```

**Benefits:**
- Handles thousands of concurrent connections
- Better query optimization for large datasets
- Advanced indexing (GiN, GiST for full-text search)
- Horizontal scaling with read replicas
- Connection pooling support

---

#### 2. API Performance Enhancements 🚀

**Pagination, Connection Pooling, and Rate Limiting**

To handle large product catalogs efficiently, the API implements pagination that returns results in manageable chunks (typically 50-100 items per request) rather than loading entire datasets into memory. Connection pooling maintains a pool of reusable database connections, dramatically reducing the overhead of establishing new connections for each request. Rate limiting protects the system from abuse by restricting the number of requests per user or IP address, ensuring fair resource distribution and system stability under high traffic.

---

#### 3. LLM Optimization 🤖

**Multi-Stage Filtering and Intelligent Product Selection**

To efficiently handle large product catalogs (10,000+ items), the system uses a multi-stage filtering and ranking pipeline. Products are first filtered by category, price range, and customer type, then ranked by relevance to select only the top 20 most suitable items for LLM processing. Each product is scored based on price compatibility, technical specifications, brand preferences, and stock availability, ensuring high-quality recommendations while minimizing LLM context usage. Frequently requested queries are cached for a short period, significantly reducing database load and 
API costs while improving response time.

**LangGraph Integration for Complex Workflows**

As the system scales and conversation flows become more sophisticated, LangGraph can be integrated to manage multi-step decision processes. Unlike simple prompt-response patterns, LangGraph enables the creation of stateful conversation graphs where the system can backtrack, maintain conversation memory across multiple turns, and handle complex decision trees.
---

#### 4. Performance Improvements ⚡

**Caching, Background Processing, and Query Optimization**

Redis caching stores frequently accessed data (product lists, category information) in memory with configurable expiration times, typically 5-15 minutes for product data. This eliminates repeated database queries for identical requests and provides sub-millisecond response times for cached data.

Large CSV uploads are processed asynchronously using FastAPI's BackgroundTasks, allowing the API to return immediately while processing continues in the background. Users receive instant confirmation that their upload was received, with processing status available through a separate endpoint.

Query optimization addresses the N+1 problem through eager loading, where related data (products and their recommendations) is fetched in a single query rather than executing hundreds of individual queries. This can reduce query count from 1,000+ to just 1-2 for typical product listing operations.

---

#### 5. Infrastructure Scaling 🏗️

**Load Balancing and Monitoring**

Multiple backend instances run behind an NGINX load balancer, distributing incoming requests across available servers. This provides both horizontal scaling (adding more servers as load increases) and high availability (if one server fails, others continue serving requests).

Production monitoring integrates Prometheus for metrics collection, Grafana for real-time visualization dashboards, Sentry for automatic error tracking and alerting, and the ELK stack (Elasticsearch, Logstash, Kibana) for centralized log aggregation and analysis. These tools provide visibility into system health, performance bottlenecks, error rates, and user behavior patterns.

---


### API Testing
Use included Postman collection:
```bash
postman collection run "Postman/SmartByte API.postman_collection.json"
```
---

**Key Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/conversation/message` | POST | Chat |
| `/api/admin/login` | POST | Login |
| `/api/admin/metrics` | GET | Metrics |
| `/api/admin/sessions` | GET | Sessions |
| `/api/admin/products/upload` | POST | CSV Upload |

---

