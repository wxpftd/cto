# Inbox Intake Pipeline

This document describes the inbox intake pipeline implementation, which provides LLM-driven classification of inbox items and automatic creation of projects and tasks.

## Features

### 1. LLM Client Abstraction
Located in `app/llm/`:
- **Base client interface** (`base.py`): Abstract base class for all LLM clients
- **OpenAI client** (`openai_client.py`): Implementation for OpenAI GPT models
- **Claude client** (`claude_client.py`): Implementation for Anthropic Claude models
- **Factory** (`factory.py`): Factory function to get the appropriate client based on configuration

The LLM client is configurable via environment variables:
```
LLM_PROVIDER=openai|claude
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
LLM_MODEL=gpt-4
LLM_MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=30
```

### 2. Inbox Service
Located in `app/services/inbox_service.py`:
- **create_inbox_item()**: Creates a new inbox item
- **classify_with_llm()**: Uses LLM to classify inbox items (with retry logic)
- **process_inbox_item()**: Complete processing pipeline that:
  - Classifies the inbox item using LLM
  - Creates projects and/or tasks based on classification
  - Updates inbox item status
  - Logs all LLM calls

### 3. API Endpoints
Located in `app/api/v1/endpoints/inbox.py`:
- **POST /api/v1/inbox/**: Create inbox item with async background processing
- **POST /api/v1/inbox/{id}/process**: Synchronously process an inbox item
- **GET /api/v1/inbox/{id}**: Get inbox item by ID

### 4. LLM Call Logging
All LLM requests are logged in the `llm_call_logs` table with:
- User ID
- Model name
- Prompt and response
- Tokens used
- Execution time
- Status (success/error/timeout)
- Error messages
- Metadata (token breakdown, etc.)

### 5. Background Processing
Uses FastAPI's `BackgroundTasks` to process inbox items asynchronously:
- Inbox item is created immediately and returned to the user
- LLM classification happens in the background
- Projects and tasks are created automatically based on classification

### 6. Retry Policy
LLM calls include automatic retry logic using `tenacity`:
- Maximum 3 retry attempts
- Exponential backoff (2-10 seconds)
- Retries on any exception
- All attempts are logged

### 7. Classification Actions
The LLM can decide on the following actions:
- **create_project**: Create a new project (for large initiatives)
- **create_task**: Create a new task with a project (for specific actions)
- **attach_to_existing**: Attach to existing project/task (not fully implemented)
- **no_action**: Just store as a note

## API Examples

### Create an Inbox Item
```bash
curl -X POST "http://localhost:8000/api/v1/inbox/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Build a new customer dashboard with real-time analytics",
    "user_id": 1,
    "tags": ["feature", "important"]
  }'
```

Response:
```json
{
  "id": 1,
  "content": "Build a new customer dashboard with real-time analytics",
  "user_id": 1,
  "project_id": null,
  "task_id": null,
  "status": "unprocessed",
  "tags": ["feature", "important"],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

The item will be automatically processed in the background.

### Process an Inbox Item Synchronously
```bash
curl -X POST "http://localhost:8000/api/v1/inbox/1/process?user_id=1"
```

Response:
```json
{
  "status": "processed",
  "inbox_item_id": 1,
  "classification": {
    "action": "create_project",
    "project_name": "Customer Dashboard",
    "project_description": "Build a new customer dashboard with real-time analytics",
    "reasoning": "This is a large initiative that warrants a full project"
  },
  "project_id": 1,
  "task_id": null
}
```

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Suites
```bash
# Test LLM clients
pytest tests/test_llm/

# Test inbox service
pytest tests/test_services/test_inbox_service.py

# Test API endpoints
pytest tests/test_api/test_inbox_endpoints.py
```

### Test Coverage
```bash
pytest --cov=app --cov-report=html
```

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Inbox Endpoint     │
│  (FastAPI)          │
└──────┬──────────────┘
       │
       ├─────────────────────────┐
       │                         │
       ▼                         ▼
┌─────────────┐         ┌────────────────┐
│  Create     │         │  Background    │
│  InboxItem  │         │  Processing    │
└──────┬──────┘         └────────┬───────┘
       │                         │
       │                         ▼
       │                  ┌─────────────────┐
       │                  │  InboxService   │
       │                  │  .process()     │
       │                  └────────┬────────┘
       │                           │
       │                           ▼
       │                  ┌─────────────────┐
       │                  │  LLM Client     │
       │                  │  (with retry)   │
       │                  └────────┬────────┘
       │                           │
       │                           ▼
       │                  ┌─────────────────┐
       │                  │  Classification │
       │                  └────────┬────────┘
       │                           │
       │                           ▼
       │                  ┌─────────────────┐
       │                  │  Create Project │
       │                  │  and/or Task    │
       │                  └────────┬────────┘
       │                           │
       ▼                           ▼
┌──────────────────────────────────────┐
│           Database                    │
│  - inbox_items                        │
│  - projects                           │
│  - tasks                              │
│  - llm_call_logs                      │
└───────────────────────────────────────┘
```

## Error Handling

1. **LLM API Errors**: Automatically retried up to 3 times with exponential backoff
2. **Parsing Errors**: Falls back to "no_action" classification if LLM response can't be parsed
3. **Database Errors**: Propagated to the API layer with appropriate HTTP status codes
4. **Missing API Keys**: Validated at startup, raises clear error messages

All errors are logged with full context for debugging.
