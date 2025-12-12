# Frontend-Backend Integration Guide

This guide explains how the frontend React application integrates with the Feedback Loop backend API.

## Architecture Overview

The project now consists of:

1. **Backend** (`/app`) - FastAPI server providing REST API endpoints
2. **Frontend** (`/frontend`) - React TypeScript application with web UI
3. **Database** - PostgreSQL for data persistence
4. **Message Queue** - Redis + Celery for async feedback processing
5. **LLM Service** - OpenAI integration for AI-powered suggestions

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│              http://localhost:5173                       │
│  • Project Management Dashboard                          │
│  • Task Editor                                           │
│  • Feedback Submission Form                              │
│  • AI Suggestions Viewer                                 │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/JSON API Calls
                         │
┌────────────────────────▼────────────────────────────────┐
│              Backend API (FastAPI)                       │
│              http://localhost:8000                       │
│  • Project Router (/projects)                            │
│  • Task Router (/tasks)                                  │
│  • Feedback Router (/feedback)                           │
└────────────────┬───────────────────────┬────────────────┘
                 │                       │
         ┌───────▼──────────┐   ┌───────▼──────────┐
         │  PostgreSQL      │   │  Redis + Celery  │
         │  Database        │   │  Message Queue   │
         └──────────────────┘   │  + LLM Service   │
                                └──────────────────┘
```

## Running the Application

### Option 1: Development with Separate Servers

Start the backend:
```bash
# Install dependencies
make install

# Setup database
make setup

# Start API (Terminal 1)
make dev

# Start Worker (Terminal 2)
make worker
```

Start the frontend:
```bash
# Install dependencies
make frontend-install

# Start dev server (Terminal 3)
make frontend-dev
```

Then open:
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

### Option 2: Using Docker Compose

Start everything with one command:
```bash
make docker-up
```

This will start:
- PostgreSQL on localhost:5432
- Redis on localhost:6379
- API on localhost:8000
- Celery Worker (background)
- Frontend on localhost:5173

View logs:
```bash
make docker-logs
```

Stop everything:
```bash
make docker-down
```

## Frontend-API Communication

### Base URL Configuration

The frontend makes API calls to the backend. Configure the API URL:

**For development:**
- Frontend uses `http://localhost:8000` (default)
- Can be customized in `frontend/.env`:
  ```
  VITE_API_URL=http://localhost:8000
  ```

**For Docker:**
- Frontend uses `http://api:8000` (internal Docker network)
- Backend sets CORS to allow all origins

### API Endpoints

The frontend communicates with these backend endpoints:

#### Projects API
```typescript
// List projects
GET /projects/?skip=0&limit=100

// Get single project with tasks
GET /projects/{id}

// Create project
POST /projects/
{ name, description, status }

// Update project
PUT /projects/{id}
{ name, description, status }

// Delete project
DELETE /projects/{id}
```

#### Tasks API
```typescript
// List tasks (optionally filter by project)
GET /tasks/?project_id={id}&skip=0&limit=100

// Get single task
GET /tasks/{id}

// Create task
POST /tasks/
{ project_id, title, description, status, priority, estimated_hours }

// Update task
PUT /tasks/{id}
{ project_id, title, description, status, priority, estimated_hours }

// Delete task
DELETE /tasks/{id}
```

#### Feedback API
```typescript
// List feedback
GET /feedback/?project_id={id}&status=completed

// Get feedback with adjustments
GET /feedback/{id}

// Submit feedback (triggers AI processing)
POST /feedback/
{ project_id, task_id, user_name, feedback_text }
```

### Client Library

Frontend API calls are organized in `src/api/`:

```typescript
// Import API functions
import { projectsAPI, tasksAPI, feedbackAPI } from '@/api'

// Use API functions
const projects = await projectsAPI.list()
const project = await projectsAPI.get(1)
const updated = await projectsAPI.update(1, { name: 'New Name' })
await projectsAPI.delete(1)

// Same patterns for tasks and feedback
```

## Data Flow: Example - Submitting Feedback

1. **User submits feedback in frontend**
   - FeedbackForm component submits data
   - Frontend calls `feedbackAPI.submit()`
   - Makes `POST /feedback/` request to backend

2. **Backend receives feedback**
   - Validates project/task existence
   - Saves feedback record to PostgreSQL
   - Queues Celery task for async processing
   - Returns feedback_id and status='pending'

3. **Frontend shows pending status**
   - Feedback appears with "Processing" spinner
   - Real feedback list will auto-refresh

4. **Celery worker processes feedback**
   - Background worker picks up task
   - Calls OpenAI API to analyze feedback
   - Generates adjustment suggestions
   - Stores adjustments in database
   - Updates feedback status to 'completed'

5. **Frontend fetches updated feedback**
   - User refreshes or auto-refresh occurs
   - `GET /feedback/{id}` returns completed feedback
   - AI suggestions display under feedback entry

## Request/Response Types

### Project
```typescript
interface Project {
  id: number
  name: string
  description?: string
  status: 'active' | 'completed' | 'on_hold' | 'cancelled'
  created_at: string
  updated_at: string
  tasks?: Task[]
}
```

### Task
```typescript
interface Task {
  id: number
  project_id: number
  title: string
  description?: string
  status: 'todo' | 'in_progress' | 'completed' | 'blocked'
  priority: number // 0-10
  estimated_hours?: number
  created_at: string
  updated_at: string
}
```

### Feedback
```typescript
interface Feedback {
  id: number
  project_id: number
  task_id?: number
  user_name?: string
  feedback_text: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  processed_at?: string
  adjustments?: Adjustment[]
}
```

### Adjustment (AI-generated)
```typescript
interface Adjustment {
  id: number
  feedback_id: number
  adjustment_type: string
  title: string
  description: string
  impact: string
  created_at: string
}
```

## Error Handling

### Frontend Error Handling

The frontend handles API errors gracefully:

```typescript
try {
  const data = await projectsAPI.create(formData)
  // Success
} catch (error) {
  // Display error message to user
  console.error(error)
}
```

### Common HTTP Status Codes

- `200 OK` - Successful GET/PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Server Error` - Backend error

## CORS Configuration

The backend has CORS enabled for all origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This allows the frontend to communicate with the backend from any origin.

## Environment Variables

### Backend (`.env`)
```
DATABASE_URL=postgresql://user:password@localhost:5432/feedback_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4
```

### Frontend (`frontend/.env`)
```
VITE_API_URL=http://localhost:8000
```

## Development Workflow

### Making Backend Changes

1. Update models in `app/models.py`
2. Create migration: `make migrate-create`
3. Run migration: `make migrate`
4. Update schemas in `app/schemas.py`
5. Update routers in `app/routers/`
6. Frontend will automatically use updated APIs

### Making Frontend Changes

1. Update API client in `src/api/`
2. Update components in `src/components/`
3. Add new pages in `src/pages/`
4. Frontend dev server auto-reloads
5. No backend restart needed

### Testing API Changes

Test APIs directly with Swagger UI:
- Visit: http://localhost:8000/docs
- Try out endpoints from the browser
- Copy curl commands from the interface

Then update frontend components to use new data.

## Debugging

### View API Logs
```bash
# If using Docker
make docker-logs

# If running locally
# Check the terminal where you ran `make dev`
```

### Browser Developer Tools

Check Network tab to see:
- API requests from frontend
- Request/response payloads
- HTTP status codes
- Response times

### API Response Format

All responses are JSON with this structure:
```json
// Success (GET list)
[
  { id: 1, name: "Project 1", ... },
  { id: 2, name: "Project 2", ... }
]

// Success (GET single/POST/PUT)
{ id: 1, name: "Project", ... }

// Success (DELETE)
No content (204)

// Error
{ "detail": "Error message" }
```

## Deployment

### Frontend Build
```bash
cd frontend
npm run build
# Creates dist/ folder with production build
```

### Serve Frontend
```bash
# Using Docker
docker build -t feedback-frontend ./frontend
docker run -p 5173:5173 feedback-frontend

# Or serve dist folder with any static server
npx serve dist
```

### Full Stack Docker Build
```bash
# Build both frontend and backend images
docker-compose build

# Run all services
docker-compose up -d
```

## Troubleshooting

### Frontend can't connect to API

1. Check backend is running: `http://localhost:8000/health`
2. Check browser console for errors
3. Verify API URL in `frontend/.env`
4. Check CORS headers in browser Network tab

### Feedback stuck in "processing"

1. Check Celery worker is running: `make worker`
2. Check Redis is available: `redis-cli ping`
3. Check worker logs for errors
4. Verify OpenAI API key is valid

### Database migration errors

```bash
# Check migration status
alembic current

# Rollback last migration
alembic downgrade -1

# Upgrade to head
alembic upgrade head
```

### API returns 404 for valid endpoints

1. Check backend is running on correct port
2. Verify CORS middleware is enabled
3. Check API documentation: http://localhost:8000/docs

## Next Steps

- Add authentication/authorization
- Implement WebSocket for real-time updates
- Add pagination UI components
- Expand AI suggestion types
- Add export/reporting features
- Implement search and filtering

See [API_REFERENCE.md](API_REFERENCE.md) for complete endpoint documentation.
