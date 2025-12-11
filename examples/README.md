# API Examples

This directory contains example JSON payloads for testing the Feedback Loop API.

## Usage with curl

### 1. Create a Project

```bash
curl -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d @examples/01_create_project.json
```

Expected response:
```json
{
  "id": 1,
  "name": "E-Commerce Platform Upgrade",
  "description": "Modernize our e-commerce platform with new features and improved performance",
  "status": "active",
  "created_at": "2024-01-15T10:00:00.000Z",
  "updated_at": "2024-01-15T10:00:00.000Z"
}
```

### 2. Create Tasks

Create each task from the array individually:

```bash
# Task 1
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Implement new product search functionality",
    "description": "Add advanced filtering and faceted search",
    "status": "in_progress",
    "priority": 7,
    "estimated_hours": 80
  }'

# Task 2
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Optimize database queries",
    "description": "Improve query performance for product listings",
    "status": "todo",
    "priority": 5,
    "estimated_hours": 40
  }'

# Task 3
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Add wishlist feature",
    "description": "Allow users to save products for later",
    "status": "todo",
    "priority": 4,
    "estimated_hours": 60
  }'

# Task 4
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Update payment gateway integration",
    "description": "Migrate to new payment provider API",
    "status": "todo",
    "priority": 9,
    "estimated_hours": 100
  }'
```

### 3. Submit Task-Specific Feedback

```bash
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d @examples/03_submit_feedback.json
```

Expected response:
```json
{
  "feedback_id": 1,
  "status": "pending",
  "message": "Feedback received and queued for processing",
  "task_id": "abc123-celery-task-id"
}
```

### 4. Submit Project-Level Feedback

```bash
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d @examples/04_project_level_feedback.json
```

### 5. Check Feedback Status

```bash
# Get specific feedback with adjustments
curl http://localhost:8000/feedback/1

# List all feedback
curl http://localhost:8000/feedback/

# Filter by project
curl "http://localhost:8000/feedback/?project_id=1"

# Filter by status
curl "http://localhost:8000/feedback/?status=completed"
```

### 6. View Project with All Tasks

```bash
curl http://localhost:8000/projects/1
```

## Expected LLM Adjustments

### For Task-Specific Feedback (03_submit_feedback.json)

The LLM should suggest adjustments like:
- Split the search task into two phases
- Increase priority of database optimization task
- Create new task for basic search functionality
- Create new task for advanced search features

### For Project-Level Feedback (04_project_level_feedback.json)

The LLM should suggest adjustments like:
- Lower priority or defer wishlist feature
- Add new task for comprehensive testing
- Adjust overall timeline expectations
- Re-prioritize critical tasks (search and payments)

## Testing the Complete Workflow

Run this bash script to test the complete workflow:

```bash
#!/bin/bash

echo "1. Creating project..."
PROJECT_ID=$(curl -s -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d @examples/01_create_project.json | jq -r '.id')
echo "Project ID: $PROJECT_ID"

echo -e "\n2. Creating tasks..."
TASK1_ID=$(curl -s -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"project_id": '"$PROJECT_ID"', "title": "Implement new product search functionality", "description": "Add advanced filtering and faceted search", "status": "in_progress", "priority": 7, "estimated_hours": 80}' | jq -r '.id')
echo "Task 1 ID: $TASK1_ID"

echo -e "\n3. Submitting feedback..."
FEEDBACK_ID=$(curl -s -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d '{"project_id": '"$PROJECT_ID"', "task_id": '"$TASK1_ID"', "user_name": "Product Manager", "feedback_text": "The search functionality is getting bogged down. We should split this into two phases."}' | jq -r '.feedback_id')
echo "Feedback ID: $FEEDBACK_ID"

echo -e "\n4. Waiting for processing..."
sleep 15

echo -e "\n5. Fetching results..."
curl -s http://localhost:8000/feedback/$FEEDBACK_ID | jq '.'
```

Save as `test_workflow.sh`, make executable (`chmod +x test_workflow.sh`), and run!
