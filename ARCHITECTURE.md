# Architecture Documentation

## System Overview

The Feedback Loop API is an intelligent project management system that uses AI to analyze user feedback and generate actionable re-planning suggestions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  (HTTP Clients, Web Apps, Mobile Apps, CLI Tools)           │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Projects   │  │    Tasks     │  │   Feedback   │      │
│  │   Router     │  │   Router     │  │   Router     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Pydantic Schemas (Validation)             │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          SQLAlchemy ORM (Database Models)           │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PostgreSQL Database                    │    │
│  │   Projects | Tasks | Feedbacks | Adjustments        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Background Processing                      │
│                                                               │
│  ┌──────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │  Redis   │◀────▶│    Celery    │─────▶│  LLM Service │  │
│  │  Broker  │      │    Worker    │      │   (OpenAI)   │  │
│  └──────────┘      └──────────────┘      └──────────────┘  │
│                            │                                 │
│                            ▼                                 │
│                    ┌──────────────┐                          │
│                    │  PostgreSQL  │                          │
│                    │  (Updates)   │                          │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Application Layer

**Purpose:** Handle HTTP requests, validation, and routing

**Components:**
- **Main Application** (`app/main.py`)
  - FastAPI instance configuration
  - CORS middleware
  - Router registration
  - API documentation setup

- **Routers** (`app/routers/`)
  - `projects.py`: CRUD operations for projects
  - `tasks.py`: CRUD operations for tasks
  - `feedback.py`: Feedback submission and retrieval with AI processing trigger

- **Schemas** (`app/schemas.py`)
  - Pydantic models for request/response validation
  - Type safety and automatic documentation

**Key Features:**
- Automatic OpenAPI/Swagger documentation
- Request validation with detailed error messages
- Type hints throughout
- RESTful API design

### 2. Data Layer

**Purpose:** Persist and retrieve data

**Components:**
- **Database Configuration** (`app/database.py`)
  - SQLAlchemy engine setup
  - Session management
  - Connection pooling

- **Models** (`app/models.py`)
  - `Project`: Top-level container
  - `Task`: Work items within projects
  - `Feedback`: User-submitted feedback
  - `Adjustment`: AI-generated suggestions
  - Enums for status types

**Relationships:**
```
Project (1) ──── (N) Task
   │
   └── (N) Feedback ──── (N) Adjustment
           │
           └── (0..1) Task
```

**Database Schema:**

```sql
-- Projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status projectstatus DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status taskstatus DEFAULT 'TODO',
    priority INTEGER DEFAULT 0,
    estimated_hours FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Feedbacks table
CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    user_name VARCHAR(255),
    feedback_text TEXT NOT NULL,
    status feedbackstatus DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

-- Adjustments table
CREATE TABLE adjustments (
    id SERIAL PRIMARY KEY,
    feedback_id INTEGER REFERENCES feedbacks(id) ON DELETE CASCADE,
    adjustment_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    original_value TEXT,
    new_value TEXT,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Background Processing Layer

**Purpose:** Asynchronously process feedback using AI

**Components:**
- **Celery Worker** (`app/workers/celery_app.py`)
  - Task queue configuration
  - Redis broker connection
  - Result backend setup

- **Tasks** (`app/workers/tasks.py`)
  - `process_feedback`: Main async task
  - Fetches context from database
  - Calls LLM service
  - Stores results

- **LLM Service** (`app/services/llm_service.py`)
  - OpenAI API integration
  - Prompt engineering
  - Response parsing
  - Error handling

**Processing Flow:**

```
1. User submits feedback via POST /feedback/
   ↓
2. Feedback saved to DB (status: pending)
   ↓
3. Celery task queued
   ↓
4. API returns immediately (feedback_id + task_id)
   ↓
5. Worker picks up task
   ↓
6. Worker fetches project + tasks context
   ↓
7. Worker calls LLM service
   ↓
8. LLM analyzes feedback in context
   ↓
9. LLM returns structured JSON with adjustments
   ↓
10. Worker parses and stores adjustments
   ↓
11. Feedback status updated (completed/failed)
   ↓
12. Client retrieves results via GET /feedback/{id}
```

### 4. LLM Integration

**Purpose:** Generate intelligent re-planning suggestions

**How It Works:**

1. **Context Building:**
   - Project details (name, description, status)
   - All current tasks (title, description, status, priority, estimates)
   - User feedback text

2. **Prompt Engineering:**
```
System: You are an intelligent project planning assistant...

User: 
Project Context:
- Name: [project name]
- Description: [description]
- Status: [status]

Current Tasks:
- Task #1: [title] (Status: [status], Priority: [priority])
- Task #2: ...

User Feedback:
[feedback text]

Based on this, suggest specific adjustments in JSON format...
```

3. **Response Format:**
```json
{
  "summary": "Brief analysis summary",
  "adjustments": [
    {
      "adjustment_type": "task_priority",
      "description": "What to change",
      "original_value": "Current value",
      "new_value": "Suggested value",
      "reasoning": "Why this makes sense",
      "task_id": "Affected task ID (if applicable)"
    }
  ]
}
```

4. **Adjustment Types:**
   - `task_priority`: Suggest priority changes
   - `task_description`: Modify task details
   - `task_status`: Change task status
   - `new_task`: Suggest creating new tasks
   - `remove_task`: Suggest removing/consolidating
   - `task_estimate`: Adjust time estimates
   - `general`: Project-level suggestions

## Data Flow Examples

### Example 1: Create Project and Tasks

```
Client → POST /projects/
  ↓
FastAPI validates request (Pydantic)
  ↓
SQLAlchemy creates Project record
  ↓
Return project with ID

Client → POST /tasks/ (x3)
  ↓
FastAPI validates + checks project exists
  ↓
SQLAlchemy creates Task records
  ↓
Return tasks with IDs
```

### Example 2: Submit and Process Feedback

```
Client → POST /feedback/
  ↓
FastAPI validates request
  ↓
Check project and task exist
  ↓
Create Feedback record (status: pending)
  ↓
Queue Celery task: process_feedback(feedback_id)
  ↓
Return feedback_id immediately
  ↓
[Async] Celery worker picks up task
  ↓
Worker: Fetch project + tasks
  ↓
Worker: Build context for LLM
  ↓
Worker: Call OpenAI API
  ↓
[External] OpenAI processes prompt
  ↓
Worker: Parse JSON response
  ↓
Worker: Create Adjustment records
  ↓
Worker: Update feedback (status: completed)
  ↓
Client → GET /feedback/{id}
  ↓
FastAPI returns feedback + adjustments
```

## Scalability Considerations

### Current Architecture
- **Single server setup** (good for 100s of requests/min)
- **Single Celery worker** (1 feedback at a time)
- **Single PostgreSQL instance**

### Scaling Strategies

**Horizontal Scaling:**
```
Load Balancer
    │
    ├── FastAPI Instance 1
    ├── FastAPI Instance 2
    └── FastAPI Instance 3
           │
           ├── Celery Worker 1
           ├── Celery Worker 2
           └── Celery Worker 3
                  │
                  ├── Redis Cluster
                  └── PostgreSQL (Primary + Replicas)
```

**Optimization Points:**
1. **API Layer:**
   - Deploy multiple FastAPI instances behind load balancer
   - Use async endpoints for I/O operations
   - Implement caching (Redis) for frequent queries

2. **Database:**
   - Add read replicas for GET operations
   - Implement connection pooling
   - Add database indexes on frequently queried fields
   - Consider partitioning for large datasets

3. **Background Processing:**
   - Scale Celery workers horizontally
   - Implement task prioritization
   - Add retry logic with exponential backoff
   - Monitor queue lengths

4. **LLM Integration:**
   - Implement response caching for similar feedback
   - Use rate limiting to respect OpenAI limits
   - Consider using GPT-3.5-turbo for cost optimization
   - Implement fallback strategies for API failures

## Security Considerations

### Current Implementation
- No authentication/authorization
- Open API endpoints
- Environment-based secrets

### Production Recommendations

1. **Authentication & Authorization:**
   - Implement JWT tokens
   - Add user roles (admin, manager, contributor)
   - API key authentication for service-to-service

2. **Data Protection:**
   - HTTPS only (TLS 1.3)
   - SQL injection protection (SQLAlchemy parameterized queries)
   - Input validation (Pydantic)
   - Rate limiting per user/IP

3. **Secrets Management:**
   - Use secret management service (AWS Secrets Manager, HashiCorp Vault)
   - Rotate API keys regularly
   - Never commit `.env` files

4. **API Security:**
   - CORS configuration (restrict origins)
   - Request size limits
   - Timeout configuration
   - Error message sanitization (don't leak internals)

## Monitoring & Observability

### Recommended Additions

1. **Logging:**
   - Structured logging (JSON format)
   - Log aggregation (ELK stack, CloudWatch)
   - Request ID tracing

2. **Metrics:**
   - Request latency (p50, p95, p99)
   - Error rates by endpoint
   - Celery queue length
   - OpenAI API call duration
   - Database query performance

3. **Alerting:**
   - High error rates
   - Slow response times
   - Celery worker failures
   - OpenAI API failures
   - Database connection issues

4. **Tracing:**
   - Distributed tracing (Jaeger, Zipkin)
   - End-to-end request tracking

## Technology Choices & Rationale

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| API Framework | FastAPI | Modern, fast, automatic docs, async support |
| Database | PostgreSQL | Robust, ACID compliance, great for relational data |
| ORM | SQLAlchemy | Mature, full-featured, type-safe |
| Migrations | Alembic | Standard with SQLAlchemy, version control for schema |
| Task Queue | Celery | Battle-tested, distributed, multiple brokers |
| Message Broker | Redis | Fast, simple, also useful for caching |
| LLM Provider | OpenAI | Best-in-class models, structured outputs |
| Validation | Pydantic | Type-safe, automatic validation, great with FastAPI |
| Server | Uvicorn | Fast ASGI server, production-ready |
| Containerization | Docker | Consistent environments, easy deployment |

## Future Enhancements

1. **Real-time Updates:**
   - WebSocket support for live feedback status
   - Server-Sent Events for progress updates

2. **Advanced AI Features:**
   - Automatic application of suggestions
   - Learning from user acceptance/rejection
   - Multi-model comparison (GPT-4 vs Claude vs Llama)

3. **Collaboration:**
   - User accounts and teams
   - Comments on feedback
   - Voting on adjustments

4. **Analytics:**
   - Feedback patterns dashboard
   - AI suggestion acceptance rates
   - Project velocity metrics

5. **Integrations:**
   - JIRA sync
   - GitHub issues integration
   - Slack notifications
   - Email digests

## Development Workflow

1. **Local Development:**
   ```bash
   docker-compose up -d  # Start dependencies
   alembic upgrade head  # Run migrations
   uvicorn app.main:app --reload  # Start API
   celery -A app.workers.celery_app worker  # Start worker
   ```

2. **Making Changes:**
   - Edit code
   - Auto-reload picks up changes
   - Test via Swagger UI
   - Create migration if models changed

3. **Testing:**
   - Run test workflow script
   - Use example JSON files
   - Check logs for errors

4. **Deployment:**
   - Build Docker images
   - Push to registry
   - Update k8s/docker-compose configs
   - Run migrations
   - Deploy new version

## Conclusion

This architecture provides:
- ✅ Separation of concerns
- ✅ Scalability paths
- ✅ Maintainability
- ✅ Type safety
- ✅ Async processing
- ✅ AI integration
- ✅ Production readiness (with enhancements)

For questions or suggestions, please refer to the main [README.md](README.md).
