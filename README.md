# Feedback Loop

An intelligent project management system with a modern web UI that captures user feedback and automatically generates re-planning suggestions using LLM (Large Language Model) analysis.

## 🚀 Features

- **Modern Web UI**: React + TypeScript frontend with Tailwind CSS
- **Project & Task Management**: Create and manage projects with associated tasks
- **Feedback Capture**: Submit user feedback linked to projects or specific tasks via the web interface
- **AI-Powered Re-planning**: Automatic analysis and adjustment suggestions using OpenAI's GPT models
- **Async Processing**: Background workers handle LLM processing via Celery
- **Adjustment Tracking**: Store and retrieve all AI-generated suggestions
- **RESTful API**: FastAPI-powered REST endpoints with automatic OpenAPI/Swagger documentation
- **Type Safety**: Full TypeScript frontend + Pydantic validation for request/response models
- **Real-time Feedback**: Live status tracking for AI-powered feedback processing

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Frontend](#frontend)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Migrations](#database-migrations)
- [Running the Application](#running-the-application)
- [Background Worker](#background-worker)
- [API Documentation](#api-documentation)
- [Example Workflows](#example-workflows)
- [LLM Configuration](#llm-configuration)
- [Development](#development)
- [Testing](#testing)

## 🏗️ Architecture

### System Components

```
┌──────────────┐     ┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser    │────▶│   Frontend  │─────▶│  FastAPI App │─────▶│  PostgreSQL │
│   (React UI) │◀────│  (React TS) │◀─────│   (REST API) │◀─────│  Database   │
└──────────────┘     └─────────────┘      └──────────────┘      └─────────────┘
  localhost:5173       localhost:3000       localhost:8000
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │    Redis     │
                                           │   (Broker)   │
                                           └──────────────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐      ┌─────────────┐
                                           │    Celery    │─────▶│   OpenAI    │
                                           │    Worker    │◀─────│   API (LLM) │
                                           └──────────────┘      └─────────────┘
```

### Tech Stack

**Frontend:**
- React 18 with TypeScript
- Tailwind CSS for styling
- React Router for navigation
- Axios for API calls
- Vite as build tool

**Backend:**
- FastAPI 0.104+ (Python 3.11+)
- PostgreSQL 15+ for data persistence
- SQLAlchemy 2.0+ ORM
- Alembic for migrations
- Celery 5.3+ for async tasks
- Redis 7+ as message broker
- OpenAI API for LLM integration
- Uvicorn (ASGI) server

### Data Models

1. **Project**: Top-level container for tasks
   - Fields: name, description, status, timestamps

2. **Task**: Individual work items within a project
   - Fields: title, description, status, priority, estimated_hours, timestamps

3. **Feedback**: User-submitted feedback
   - Fields: project_id, task_id (optional), user_name, feedback_text, status, timestamps

4. **Adjustment**: LLM-generated suggestions
   - Fields: feedback_id, adjustment_type, description, original_value, new_value, reasoning

## 📦 Prerequisites

- Python 3.11 or higher
- Node.js 16+ and npm/yarn
- PostgreSQL 15 or higher
- Redis 7 or higher
- OpenAI API key
- Docker & Docker Compose (recommended for local development)

## 🚀 Quick Start

### Using Docker Compose (Easiest)

```bash
# Clone and setup
git clone <repository-url>
cd feedback-loop
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env

# Start all services (API, Frontend, Database, Workers)
make docker-up

# Services will be available at:
# - Frontend: http://localhost:5173
# - API Docs: http://localhost:8000/docs
```

### Using Make Commands

```bash
# Backend only
make install
make setup
make dev      # Terminal 1 - API server
make worker   # Terminal 2 - Background worker

# Frontend (in new terminal)
make frontend-install
make frontend-dev
```

## 🎨 Frontend

The project now includes a complete React + TypeScript frontend!

**Features:**
- Project dashboard with create/edit/delete
- Task management with priority and status tracking
- Feedback submission form
- Real-time AI suggestion viewer
- Responsive design with Tailwind CSS

**Quick Start:**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

For detailed frontend documentation, see [frontend/README.md](frontend/README.md)

For integration details, see [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

## 🔧 Installation

### Option 1: Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd feedback-loop-api
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

4. Start all services:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
docker-compose exec api alembic upgrade head
```

6. Access the API:
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Option 2: Local Development

1. Clone and navigate to the repository:
```bash
git clone <repository-url>
cd feedback-loop-api
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL and Redis (using Docker):
```bash
docker run -d --name feedback_postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=feedback_db \
  -p 5432:5432 \
  postgres:15-alpine

docker run -d --name feedback_redis \
  -p 6379:6379 \
  redis:7-alpine
```

5. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

6. Run migrations:
```bash
alembic upgrade head
```

7. Start the API server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

8. Start Celery worker (in a separate terminal):
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## ⚙️ Configuration

### Environment Variables

All configuration is managed through environment variables. See `.env.example` for all available options:

#### Database Configuration
```env
DATABASE_URL=postgresql://user:password@localhost:5432/feedback_db
```

#### Redis Configuration
```env
REDIS_URL=redis://localhost:6379/0
```

#### OpenAI Configuration
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_API_URL=  # Optional: Custom base URL (e.g., https://openrouter.ai/api/v1 for OpenRouter)
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo for lower costs
```

**Using OpenRouter or Other Compatible APIs:**

To use [OpenRouter](https://openrouter.ai/) or other OpenAI-compatible APIs, set the `OPENAI_API_URL`:

```env
# For OpenRouter
OPENAI_API_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
OPENAI_MODEL=anthropic/claude-3-opus  # Or any model available on OpenRouter

# For other custom endpoints
OPENAI_API_URL=https://your-custom-api.com/v1
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=your-model-name
```

#### Application Settings
```env
APP_NAME=Feedback Loop API
APP_VERSION=1.0.0
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
```

#### Celery Configuration
```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### LLM Configuration
```env
LLM_MAX_TOKENS=2000        # Maximum tokens in LLM response
LLM_TEMPERATURE=0.7        # 0.0 = deterministic, 1.0 = creative
LLM_TIMEOUT=60            # Request timeout in seconds
```

## 🗄️ Database Migrations

This project uses Alembic for database migrations.

### Creating a New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision_id>

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>
```

### Checking Migration Status

```bash
alembic current
alembic history
```

## 🚀 Running the Application

### Development Mode

```bash
# API Server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Celery Worker with auto-reload
watchmedo auto-restart --directory=./app --pattern=*.py --recursive -- \
  celery -A app.workers.celery_app worker --loglevel=info
```

### Production Mode

```bash
# API Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Celery Worker
celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

## 👷 Background Worker

The Celery worker handles asynchronous LLM processing of feedback.

### How It Works

1. User submits feedback via POST `/feedback/`
2. Feedback is saved to database with status `PENDING`
3. Celery task is queued to process the feedback
4. API returns immediately with feedback ID and task ID
5. Worker picks up the task and:
   - Fetches project and task context
   - Calls OpenAI API with structured prompt
   - Parses LLM response
   - Creates adjustment records
   - Updates feedback status to `COMPLETED` or `FAILED`

### Monitoring Workers

```bash
# Check worker status
celery -A app.workers.celery_app inspect active

# Check registered tasks
celery -A app.workers.celery_app inspect registered

# Check task stats
celery -A app.workers.celery_app inspect stats
```

### Task Configuration

Worker settings in `app/workers/celery_app.py`:
- **task_time_limit**: 300 seconds (hard limit)
- **task_soft_time_limit**: 240 seconds (soft limit, raises exception)
- **task_track_started**: Enabled for monitoring
- **timezone**: UTC

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Projects

```
POST   /projects/           Create a new project
GET    /projects/           List all projects
GET    /projects/{id}       Get project details with tasks
PUT    /projects/{id}       Update project
DELETE /projects/{id}       Delete project
```

#### Tasks

```
POST   /tasks/              Create a new task
GET    /tasks/              List all tasks (filter by project_id)
GET    /tasks/{id}          Get task details
PUT    /tasks/{id}          Update task
DELETE /tasks/{id}          Delete task
```

#### Feedback (Primary Feature)

```
POST   /feedback/           Submit feedback and trigger re-planning
GET    /feedback/           List feedback (filter by project, task, status)
GET    /feedback/{id}       Get feedback with all adjustments
DELETE /feedback/{id}       Delete feedback
```

## 🎯 Example Workflows

### Complete End-to-End Example

#### 1. Create a Project

```bash
curl -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App Redesign",
    "description": "Complete redesign of our mobile application",
    "status": "active"
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Mobile App Redesign",
  "description": "Complete redesign of our mobile application",
  "status": "active",
  "created_at": "2024-01-15T10:00:00.000Z",
  "updated_at": "2024-01-15T10:00:00.000Z"
}
```

#### 2. Create Tasks

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Design new UI mockups",
    "description": "Create mockups for all main screens",
    "status": "in_progress",
    "priority": 5,
    "estimated_hours": 40
  }'

curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Implement authentication flow",
    "description": "Build login, signup, and password reset",
    "status": "todo",
    "priority": 3,
    "estimated_hours": 60
  }'
```

#### 3. Submit Feedback

```bash
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "task_id": 1,
    "user_name": "Sarah Johnson",
    "feedback_text": "The UI mockup task is taking much longer than expected. We need to prioritize the authentication flow instead because our security audit is coming up next week. Also, we should break down the UI work into smaller, more manageable pieces."
  }'
```

Response:
```json
{
  "feedback_id": 1,
  "status": "pending",
  "message": "Feedback received and queued for processing",
  "task_id": "abc123-task-id-from-celery"
}
```

#### 4. Wait for Processing (2-30 seconds depending on LLM)

The background worker will:
- Analyze the feedback in context
- Generate specific, actionable adjustments
- Store results in the database

#### 5. Retrieve Results

```bash
curl http://localhost:8000/feedback/1
```

Response:
```json
{
  "id": 1,
  "project_id": 1,
  "task_id": 1,
  "user_name": "Sarah Johnson",
  "feedback_text": "The UI mockup task is taking much longer...",
  "status": "completed",
  "created_at": "2024-01-15T10:00:00.000Z",
  "processed_at": "2024-01-15T10:00:23.000Z",
  "adjustments": [
    {
      "id": 1,
      "feedback_id": 1,
      "adjustment_type": "task_priority",
      "description": "Increase priority of authentication flow task",
      "original_value": "3",
      "new_value": "9",
      "reasoning": "Security audit is time-sensitive and authentication is a critical dependency",
      "created_at": "2024-01-15T10:00:23.000Z"
    },
    {
      "id": 2,
      "feedback_id": 1,
      "adjustment_type": "new_task",
      "description": "Create subtask: Design login screen mockup",
      "original_value": null,
      "new_value": "Break UI mockups into smaller tasks starting with login screen",
      "reasoning": "Breaking down the large UI task into smaller pieces will improve manageability",
      "created_at": "2024-01-15T10:00:23.000Z"
    },
    {
      "id": 3,
      "feedback_id": 1,
      "adjustment_type": "new_task",
      "description": "Create subtask: Design dashboard mockup",
      "original_value": null,
      "new_value": "Separate dashboard design from main UI task",
      "reasoning": "Parallel work on different screens will speed up overall progress",
      "created_at": "2024-01-15T10:00:23.000Z"
    }
  ]
}
```

#### 6. Apply Adjustments (Manual or Automated)

Based on the adjustments, you can:
- Update task priorities
- Create new tasks
- Modify task descriptions
- Change task statuses

Example - Apply priority change:
```bash
curl -X PUT http://localhost:8000/tasks/2 \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Implement authentication flow",
    "description": "Build login, signup, and password reset",
    "status": "in_progress",
    "priority": 9,
    "estimated_hours": 60
  }'
```

### Additional Examples

#### Query Feedback by Status

```bash
# Get all completed feedback
curl "http://localhost:8000/feedback/?status=completed"

# Get all pending feedback for a project
curl "http://localhost:8000/feedback/?project_id=1&status=pending"
```

#### Project-Level Feedback (No Specific Task)

```bash
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "user_name": "Alex Chen",
    "feedback_text": "The overall timeline seems too aggressive. We need to add buffer time for QA and user testing."
  }'
```

## 🤖 LLM Configuration

### Choosing a Model

The system supports any OpenAI chat model:

**GPT-4** (Recommended for production):
- Most accurate and nuanced responses
- Better context understanding
- Higher cost (~$0.03/1K tokens)
```env
OPENAI_MODEL=gpt-4
```

**GPT-3.5-Turbo** (Good for development/testing):
- Faster responses
- Lower cost (~$0.002/1K tokens)
- Still produces good results
```env
OPENAI_MODEL=gpt-3.5-turbo
```

### Tuning Parameters

**Temperature** (0.0 - 1.0):
- Lower (0.3-0.5): More consistent, focused responses
- Higher (0.7-0.9): More creative, varied suggestions
```env
LLM_TEMPERATURE=0.7
```

**Max Tokens**:
- Controls response length
- Recommended: 1500-2500 for detailed adjustments
```env
LLM_MAX_TOKENS=2000
```

### Prompt Engineering

The LLM prompt is constructed in `app/services/llm_service.py`. It includes:
- Project context (name, description, status)
- All current tasks with details
- User's feedback text
- Structured JSON output format specification

To customize the prompt:
1. Edit `_build_replan_prompt()` method
2. Modify the system message for different behavior
3. Adjust the JSON schema in the prompt

### Cost Optimization

1. **Use GPT-3.5-Turbo** for non-critical environments
2. **Reduce MAX_TOKENS** if adjustments are consistently shorter
3. **Implement caching** for similar feedback patterns
4. **Add rate limiting** to prevent abuse
5. **Set up usage monitoring** via OpenAI dashboard

### Error Handling

The system handles LLM errors gracefully:
- API timeouts: Marked as `FAILED`, can be retried
- Invalid responses: Logged and marked as `FAILED`
- API key issues: Fails fast with clear error messages
- Rate limits: Respects OpenAI rate limits, will retry

## 🛠️ Development

### Project Structure

```
feedback-loop-api/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py                  # Alembic environment
│   └── script.py.mako          # Migration template
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routers/                # API route handlers
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   └── feedback.py
│   ├── services/               # Business logic
│   │   └── llm_service.py
│   └── workers/                # Background tasks
│       ├── celery_app.py
│       └── tasks.py
├── .env                        # Environment variables (not in git)
├── .env.example                # Environment template
├── .gitignore
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Container definition
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

### Code Style

- Follow PEP 8 style guide
- Use type hints for all functions
- Document complex logic with comments
- Write descriptive commit messages

### Adding New Features

1. **New endpoint**: Add to appropriate router in `app/routers/`
2. **New model**: Update `app/models.py` and create migration
3. **New schema**: Add to `app/schemas.py`
4. **New background task**: Add to `app/workers/tasks.py`

## 🧪 Testing

### Manual Testing with Swagger UI

1. Navigate to http://localhost:8000/docs
2. Use the interactive interface to test endpoints
3. View request/response schemas
4. Try different parameter combinations

### Testing with curl

See the [Example Workflows](#example-workflows) section for comprehensive curl examples.

### Unit Testing (Future Enhancement)

Structure for future test implementation:

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_api/
│   ├── test_projects.py
│   ├── test_tasks.py
│   └── test_feedback.py
├── test_services/
│   └── test_llm_service.py
└── test_workers/
    └── test_tasks.py
```

## 🚨 Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection
psql postgresql://user:password@localhost:5432/feedback_db
```

**Redis connection errors:**
```bash
# Check if Redis is running
docker ps | grep redis

# Test connection
redis-cli ping
```

**Celery worker not processing:**
```bash
# Check worker logs
docker-compose logs celery_worker

# Check if tasks are registered
celery -A app.workers.celery_app inspect registered
```

**OpenAI API errors:**
- Verify API key is correct in `.env`
- Check OpenAI account has credits
- Verify model name is correct
- Check rate limits in OpenAI dashboard

**Migrations fail:**
```bash
# Reset to base and reapply
alembic downgrade base
alembic upgrade head
```

## 📝 License

[Your License Here]

## 🤝 Contributing

[Your Contributing Guidelines Here]

## 📧 Support

[Your Support Information Here]

---

**Happy Coding!** 🎉
