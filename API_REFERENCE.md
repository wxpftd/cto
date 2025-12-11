# API Reference

Complete reference for all Feedback Loop API endpoints.

Base URL: `http://localhost:8000`

## Table of Contents

- [Projects](#projects)
- [Tasks](#tasks)
- [Feedback](#feedback)
- [Health](#health)
- [Error Responses](#error-responses)

---

## Projects

### Create Project

Create a new project.

**Endpoint:** `POST /projects/`

**Request Body:**
```json
{
  "name": "string (required, 1-255 chars)",
  "description": "string (optional)",
  "status": "active|completed|on_hold|cancelled (optional, default: active)"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign",
    "description": "Complete overhaul of company website",
    "status": "active"
  }'
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Website Redesign",
  "description": "Complete overhaul of company website",
  "status": "active",
  "created_at": "2024-01-15T10:00:00.000000",
  "updated_at": "2024-01-15T10:00:00.000000"
}
```

---

### List Projects

Get all projects with pagination.

**Endpoint:** `GET /projects/`

**Query Parameters:**
- `skip` (integer, default: 0) - Number of records to skip
- `limit` (integer, default: 100, max: 100) - Number of records to return

**Example:**
```bash
curl http://localhost:8000/projects/?skip=0&limit=10
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Website Redesign",
    "description": "Complete overhaul of company website",
    "status": "active",
    "created_at": "2024-01-15T10:00:00.000000",
    "updated_at": "2024-01-15T10:00:00.000000"
  }
]
```

---

### Get Project

Get a single project with all its tasks.

**Endpoint:** `GET /projects/{project_id}`

**Path Parameters:**
- `project_id` (integer, required) - Project ID

**Example:**
```bash
curl http://localhost:8000/projects/1
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Website Redesign",
  "description": "Complete overhaul of company website",
  "status": "active",
  "created_at": "2024-01-15T10:00:00.000000",
  "updated_at": "2024-01-15T10:00:00.000000",
  "tasks": [
    {
      "id": 1,
      "project_id": 1,
      "title": "Design homepage mockup",
      "description": "Create mockup in Figma",
      "status": "in_progress",
      "priority": 8,
      "estimated_hours": 20.0,
      "created_at": "2024-01-15T10:05:00.000000",
      "updated_at": "2024-01-15T10:05:00.000000"
    }
  ]
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Project not found"
}
```

---

### Update Project

Update an existing project.

**Endpoint:** `PUT /projects/{project_id}`

**Path Parameters:**
- `project_id` (integer, required) - Project ID

**Request Body:** Same as Create Project

**Example:**
```bash
curl -X PUT http://localhost:8000/projects/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign (Updated)",
    "description": "Updated description",
    "status": "active"
  }'
```

**Response:** `200 OK` (same structure as Get Project)

---

### Delete Project

Delete a project and all its tasks, feedback, and adjustments.

**Endpoint:** `DELETE /projects/{project_id}`

**Path Parameters:**
- `project_id` (integer, required) - Project ID

**Example:**
```bash
curl -X DELETE http://localhost:8000/projects/1
```

**Response:** `204 No Content`

---

## Tasks

### Create Task

Create a new task within a project.

**Endpoint:** `POST /tasks/`

**Request Body:**
```json
{
  "project_id": 1,
  "title": "string (required, 1-255 chars)",
  "description": "string (optional)",
  "status": "todo|in_progress|completed|blocked (optional, default: todo)",
  "priority": 0-10 (optional, default: 0),
  "estimated_hours": "float > 0 (optional)"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Implement contact form",
    "description": "Build contact form with validation",
    "status": "todo",
    "priority": 7,
    "estimated_hours": 15.5
  }'
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "project_id": 1,
  "title": "Implement contact form",
  "description": "Build contact form with validation",
  "status": "todo",
  "priority": 7,
  "estimated_hours": 15.5,
  "created_at": "2024-01-15T10:10:00.000000",
  "updated_at": "2024-01-15T10:10:00.000000"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Project not found"
}
```

---

### List Tasks

Get all tasks with optional filtering.

**Endpoint:** `GET /tasks/`

**Query Parameters:**
- `project_id` (integer, optional) - Filter by project
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 100) - Max results

**Example:**
```bash
# All tasks
curl http://localhost:8000/tasks/

# Tasks for specific project
curl http://localhost:8000/tasks/?project_id=1

# With pagination
curl http://localhost:8000/tasks/?skip=10&limit=20
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "project_id": 1,
    "title": "Implement contact form",
    "description": "Build contact form with validation",
    "status": "todo",
    "priority": 7,
    "estimated_hours": 15.5,
    "created_at": "2024-01-15T10:10:00.000000",
    "updated_at": "2024-01-15T10:10:00.000000"
  }
]
```

---

### Get Task

Get a single task.

**Endpoint:** `GET /tasks/{task_id}`

**Path Parameters:**
- `task_id` (integer, required) - Task ID

**Example:**
```bash
curl http://localhost:8000/tasks/1
```

**Response:** `200 OK` (same structure as Create Task response)

---

### Update Task

Update an existing task.

**Endpoint:** `PUT /tasks/{task_id}`

**Path Parameters:**
- `task_id` (integer, required) - Task ID

**Request Body:** Same as Create Task

**Example:**
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Implement contact form",
    "description": "Build contact form with validation and spam protection",
    "status": "in_progress",
    "priority": 9,
    "estimated_hours": 20.0
  }'
```

**Response:** `200 OK`

---

### Delete Task

Delete a task and all its feedback.

**Endpoint:** `DELETE /tasks/{task_id}`

**Path Parameters:**
- `task_id` (integer, required) - Task ID

**Example:**
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

**Response:** `204 No Content`

---

## Feedback

### Submit Feedback

Submit user feedback for a project or task and trigger AI re-planning.

**Endpoint:** `POST /feedback/`

**Request Body:**
```json
{
  "project_id": 1,
  "task_id": 1 (optional),
  "user_name": "string (optional, max 255 chars)",
  "feedback_text": "string (required)"
}
```

**Example - Task-specific feedback:**
```bash
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "task_id": 1,
    "user_name": "Alice Smith",
    "feedback_text": "This task is taking too long. We should break it into smaller pieces and prioritize the critical features first."
  }'
```

**Example - Project-level feedback:**
```bash
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "user_name": "Bob Johnson",
    "feedback_text": "The overall timeline is too aggressive. We need to add more testing time and reduce scope for this quarter."
  }'
```

**Response:** `201 Created`
```json
{
  "feedback_id": 1,
  "status": "pending",
  "message": "Feedback received and queued for processing",
  "task_id": "abc123-celery-task-id"
}
```

**Processing Flow:**
1. Feedback saved with status `pending`
2. Celery task queued
3. Background worker processes feedback
4. Worker calls OpenAI API
5. Adjustments stored in database
6. Status updated to `completed` or `failed`

**Error Responses:**

`404 Not Found` - Project doesn't exist:
```json
{
  "detail": "Project not found"
}
```

`404 Not Found` - Task doesn't exist:
```json
{
  "detail": "Task not found"
}
```

`400 Bad Request` - Task doesn't belong to project:
```json
{
  "detail": "Task does not belong to the specified project"
}
```

---

### List Feedback

Get all feedback entries with filtering.

**Endpoint:** `GET /feedback/`

**Query Parameters:**
- `project_id` (integer, optional) - Filter by project
- `task_id` (integer, optional) - Filter by task
- `status` (string, optional) - Filter by status: `pending`, `processing`, `completed`, `failed`
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 100) - Max results

**Examples:**
```bash
# All feedback
curl http://localhost:8000/feedback/

# Feedback for specific project
curl "http://localhost:8000/feedback/?project_id=1"

# Completed feedback only
curl "http://localhost:8000/feedback/?status=completed"

# Pending feedback for specific task
curl "http://localhost:8000/feedback/?task_id=1&status=pending"

# With pagination
curl "http://localhost:8000/feedback/?skip=10&limit=20"
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "project_id": 1,
    "task_id": 1,
    "user_name": "Alice Smith",
    "feedback_text": "This task is taking too long...",
    "status": "completed",
    "created_at": "2024-01-15T10:00:00.000000",
    "processed_at": "2024-01-15T10:00:23.000000"
  }
]
```

---

### Get Feedback

Get detailed feedback information including all AI-generated adjustments.

**Endpoint:** `GET /feedback/{feedback_id}`

**Path Parameters:**
- `feedback_id` (integer, required) - Feedback ID

**Example:**
```bash
curl http://localhost:8000/feedback/1
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "project_id": 1,
  "task_id": 1,
  "user_name": "Alice Smith",
  "feedback_text": "This task is taking too long. We should break it into smaller pieces and prioritize the critical features first.",
  "status": "completed",
  "created_at": "2024-01-15T10:00:00.000000",
  "processed_at": "2024-01-15T10:00:23.000000",
  "adjustments": [
    {
      "id": 1,
      "feedback_id": 1,
      "adjustment_type": "task_priority",
      "description": "Increase priority of critical features",
      "original_value": "5",
      "new_value": "9",
      "reasoning": "Based on feedback, critical features should be prioritized to meet user needs faster",
      "created_at": "2024-01-15T10:00:23.000000"
    },
    {
      "id": 2,
      "feedback_id": 1,
      "adjustment_type": "new_task",
      "description": "Create subtask for core functionality",
      "original_value": null,
      "new_value": "Implement minimal viable version of feature",
      "reasoning": "Breaking down the large task will make it more manageable and allow faster delivery",
      "created_at": "2024-01-15T10:00:23.000000"
    }
  ]
}
```

**Adjustment Types:**
- `task_priority` - Change task priority
- `task_description` - Modify task description
- `task_status` - Change task status
- `new_task` - Suggest creating a new task
- `remove_task` - Suggest removing/consolidating a task
- `task_estimate` - Adjust time estimates
- `general` - General project-level suggestions

**Status Values:**
- `pending` - Feedback received, not yet processed
- `processing` - Currently being analyzed by AI
- `completed` - Successfully processed with adjustments
- `failed` - Processing failed (check logs)

---

### Delete Feedback

Delete feedback and all associated adjustments.

**Endpoint:** `DELETE /feedback/{feedback_id}`

**Path Parameters:**
- `feedback_id` (integer, required) - Feedback ID

**Example:**
```bash
curl -X DELETE http://localhost:8000/feedback/1
```

**Response:** `204 No Content`

---

## Health

### Root Endpoint

Get API information.

**Endpoint:** `GET /`

**Example:**
```bash
curl http://localhost:8000/
```

**Response:** `200 OK`
```json
{
  "message": "Feedback Loop API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

### Health Check

Check API health status.

**Endpoint:** `GET /health`

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

---

## Error Responses

### Standard Error Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Validation Errors

When request data fails validation:

**Response:** `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Interactive Documentation

For interactive API documentation with "Try it out" functionality:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide:
- Complete endpoint documentation
- Request/response schemas
- Interactive testing interface
- Example values
- Authentication (when implemented)

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider:
- Implementing rate limiting middleware
- Setting up API keys
- Monitoring OpenAI API usage
- Adding request throttling

---

## Best Practices

1. **Always validate project_id exists** before creating tasks or feedback
2. **Include task_id** when feedback is specific to a task
3. **Poll GET /feedback/{id}** after submission to get results
4. **Use descriptive feedback_text** for better AI suggestions
5. **Check feedback status** before expecting adjustments
6. **Handle 404 errors** gracefully in your client
7. **Monitor OpenAI costs** in production

---

## Examples

See [examples/README.md](examples/README.md) for complete workflow examples with sample data.
