# Planning and Daily View

This document describes the planning and daily view functionality for project management.

## Overview

The planning system provides two main capabilities:
1. **Project Planning** - Generate comprehensive project plans with roadmap steps and milestones using LLM
2. **Daily Planning** - Automatically select and track daily "top three" tasks based on priority and status

## Features

### Project Planning (PlanVersion)

#### Plan Generation
- Automatically generates project plans after inbox classification creates a project
- Can be manually triggered or re-triggered at any time
- Uses LLM to analyze project and existing tasks to create comprehensive plans
- Tracks plan versions for history and evolution

#### Plan Content Structure
Plans are stored as JSON with the following structure:
```json
{
  "summary": "Brief summary of the project plan",
  "goals": ["goal1", "goal2", "goal3"],
  "roadmap_steps": [
    {
      "step_number": 1,
      "title": "Step title",
      "description": "What needs to be done",
      "estimated_duration": "1 week",
      "dependencies": []
    }
  ],
  "milestones": [
    {
      "title": "Milestone name",
      "target_date": "relative time like 'end of month 1'",
      "deliverables": ["deliverable1", "deliverable2"]
    }
  ],
  "risks": ["risk1", "risk2"],
  "next_steps": ["action1", "action2", "action3"]
}
```

### Daily Planning

#### Task Selection Algorithm
The daily planning service automatically selects up to 3 tasks for each day based on:

**Priority Scoring:**
- Urgent: 40 points base
- High: 30 points base
- Medium: 20 points base
- Low: 10 points base

**Status Bonus:**
- In Progress: +15 points (to encourage completion)

**Due Date Scoring:**
- Overdue: +50 points
- Due today: +40 points
- Due in 1-3 days: +30 points
- Due in 4-7 days: +20 points
- Due in 8-14 days: +10 points

**Age Bonus:**
- Tasks older than 30 days: +5 points (prevent stagnation)

#### Daily Summary Features
- Automatically creates DailySummary entries for selected tasks
- Tracks task completion status
- Records hours worked per task
- Provides formatted summary text with emojis and due date info

## API Endpoints

### Project Planning

#### Generate Plan
```
POST /api/v1/planning/generate
{
  "project_id": 1,
  "user_id": 1,
  "force_regenerate": false
}
```
Creates a new plan version for a project. If `force_regenerate` is false and a plan already exists, returns the existing plan.

#### Get Latest Plan
```
GET /api/v1/planning/projects/{project_id}/latest
```
Returns the latest plan version for a project.

#### Get Plan Content
```
GET /api/v1/planning/projects/{project_id}/content
```
Returns the parsed JSON content of the latest plan.

### Daily Planning

#### Generate Daily Plan
```
POST /api/v1/planning/daily/generate
{
  "user_id": 1,
  "target_date": "2024-12-11T00:00:00"  // optional, defaults to today
}
```
Generates a daily plan with top 3 tasks for the specified date.

#### Get Today's Plan
```
GET /api/v1/planning/daily/today/{user_id}
```
Returns today's plan for a user. Automatically generates if it doesn't exist.

#### Mark Task Complete
```
POST /api/v1/planning/tasks/complete
{
  "task_id": 1,
  "user_id": 1,
  "hours_worked": 120  // optional, in minutes
}
```
Marks a task as complete and updates the daily summary.

#### Get Daily Summary
```
GET /api/v1/planning/daily/summary/{user_id}?date=2024-12-11T00:00:00
```
Returns a summary of the daily plan including completion rate and hours worked.

Response:
```json
{
  "date": "2024-12-11",
  "total_tasks": 3,
  "completed_tasks": 2,
  "completion_rate": 66.67,
  "total_hours_worked": 180,
  "summaries": [
    {
      "id": 1,
      "summary_text": "#1 🔥 Fix critical bug (DUE TODAY)",
      "task_id": 5,
      "completed": true,
      "hours_worked": 90
    }
  ]
}
```

## Automatic Triggers

### After Inbox Classification
When the inbox service processes an item and creates a project, planning is automatically triggered:

1. InboxItem is classified by LLM
2. If classification creates a project:
   - Project is created in database
   - PlanningService.generate_project_plan() is called automatically
   - Plan version is created and stored
3. Process returns with `plan_generated: true` in response

This can be disabled by passing `trigger_planning=False` to `process_inbox_item()`.

## Business Rules

### Planning Service Rules
1. Plans are versioned - each regeneration creates a new version
2. Without force_regenerate, existing plans are returned unchanged
3. Plans are project-specific (not task-specific in this implementation)
4. LLM calls are retried up to 3 times with exponential backoff
5. All LLM calls are logged for audit and cost tracking

### Daily Planning Rules
1. Only pending and in_progress tasks are considered
2. Completed tasks are excluded from selection
3. Only tasks assigned to the requesting user are selected
4. Daily plans are created once per day per user
5. Marking a task complete updates the daily summary automatically
6. Maximum of 3 tasks per daily plan

## Service-Level Tests

### Planning Service Tests
- Plan generation with valid LLM responses
- Plan parsing with various JSON formats
- Version incrementing on regeneration
- Handling of missing/invalid data
- LLM error handling and logging
- Empty project/task scenarios

### Daily Planning Service Tests
- Task scoring algorithm for different priorities
- Task selection with various statuses
- Due date handling (overdue, today, future)
- Daily plan generation and caching
- Task completion workflow
- Summary aggregation
- Edge cases (no tasks, wrong user, etc.)

### API Integration Tests
- All endpoint success scenarios
- Error handling (404, 500)
- Parameter validation
- Multiple user isolation
- Date-specific queries

## Usage Examples

### Manual Plan Generation
```python
from app.services.planning_service import PlanningService

service = PlanningService(db)
plan = await service.generate_project_plan(
    project_id=1,
    user_id=1,
    force_regenerate=True
)
```

### Daily Planning Workflow
```python
from app.services.daily_planning_service import DailyPlanningService

service = DailyPlanningService(db)

# Get today's plan (auto-generates if needed)
plan = await service.get_today_plan(user_id=1)

# Mark a task complete
task = await service.mark_task_complete(
    task_id=5,
    user_id=1,
    hours_worked=120
)

# Get summary
summary = await service.get_plan_summary(user_id=1, date=datetime.now())
```

## Implementation Notes

### Database Models Used
- **PlanVersion**: Stores versioned project plans
- **DailySummary**: Stores daily task selections and progress
- **Task**: Source of tasks for planning
- **Project**: Associated with plan versions
- **LlmCallLog**: Tracks all LLM API calls

### LLM Integration
- Uses same LLM client factory as inbox classification
- Configurable temperature (0.5 for planning vs 0.3 for classification)
- Higher token limits for plan generation (1500 vs 500)
- Structured JSON prompts with detailed guidelines

### Performance Considerations
- Daily plans are cached per user per day
- LLM calls only when generating new plans
- Task scoring is in-memory calculation
- Database queries use indexes on user_id, date, status
