# Quick Start Guide

Get up and running with the Feedback Loop API in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Steps

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd feedback-loop-api

# Copy environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your favorite editor
```

Update this line in `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Start Everything

```bash
# Start all services (PostgreSQL, Redis, API, Celery Worker)
docker-compose up -d

# Wait for services to start (about 10 seconds)
sleep 10

# Run database migrations
docker-compose exec api alembic upgrade head
```

### 3. Verify It's Running

Open your browser to:
- **API Documentation**: http://localhost:8000/docs
- **API Root**: http://localhost:8000

You should see the interactive Swagger UI!

### 4. Create Your First Project

Using the Swagger UI at http://localhost:8000/docs:

1. Expand `POST /projects/`
2. Click "Try it out"
3. Use this example:
```json
{
  "name": "My First Project",
  "description": "Testing the feedback loop",
  "status": "active"
}
```
4. Click "Execute"
5. Note the `id` in the response (you'll need it!)

### 5. Create a Task

1. Expand `POST /tasks/`
2. Click "Try it out"
3. Use this example (replace `project_id` with your project's ID):
```json
{
  "project_id": 1,
  "title": "Build authentication system",
  "description": "Implement login and signup",
  "status": "in_progress",
  "priority": 8,
  "estimated_hours": 40
}
```
4. Click "Execute"

### 6. Submit Feedback (The Magic Happens Here! ✨)

1. Expand `POST /feedback/`
2. Click "Try it out"
3. Use this example:
```json
{
  "project_id": 1,
  "task_id": 1,
  "user_name": "Your Name",
  "feedback_text": "This authentication task is too big and blocking other work. Can we break it into smaller pieces? Also, we should prioritize the login functionality over signup since users are waiting."
}
```
4. Click "Execute"
5. Note the `feedback_id` in the response

### 7. Wait for AI Processing

The background worker is now:
- Analyzing your feedback
- Understanding project context
- Generating specific adjustments

**Wait 10-30 seconds** (depending on OpenAI API speed)

### 8. View the Results

1. Expand `GET /feedback/{feedback_id}`
2. Click "Try it out"
3. Enter your feedback ID
4. Click "Execute"

You'll see:
- Your original feedback
- Status: "completed"
- **Adjustments**: AI-generated suggestions with reasoning!

Example adjustments might include:
- "Split authentication task into 'Login' and 'Signup' tasks"
- "Increase priority of login functionality"
- "Create new task: 'Setup authentication database schema'"

## What's Happening?

```
Your Feedback → FastAPI Endpoint → Celery Queue → Background Worker
                                                          ↓
                                                   OpenAI GPT-4
                                                          ↓
AI Adjustments ← Database ← Worker Processes Response ←─┘
```

## View Logs

```bash
# API logs
docker-compose logs -f api

# Worker logs (see the AI processing happen!)
docker-compose logs -f celery_worker

# All logs
docker-compose logs -f
```

## Common Commands

```bash
# Stop everything
docker-compose down

# Restart a service
docker-compose restart api
docker-compose restart celery_worker

# View running containers
docker-compose ps

# Access API container shell
docker-compose exec api /bin/bash

# Access database
docker-compose exec postgres psql -U user feedback_db
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [examples/README.md](examples/README.md) for more use cases
- Explore the API at http://localhost:8000/docs
- Try different types of feedback to see how the AI responds
- Customize the LLM prompt in `app/services/llm_service.py`

## Troubleshooting

### "Connection refused" errors
```bash
# Check if services are running
docker-compose ps

# Restart services
docker-compose restart
```

### Worker not processing feedback
```bash
# Check worker logs
docker-compose logs celery_worker

# Verify Redis is running
docker-compose exec redis redis-cli ping
```

### OpenAI API errors
- Verify your API key in `.env`
- Check you have credits: https://platform.openai.com/account/usage
- Try switching to `gpt-3.5-turbo` in `.env` for lower costs

### Database errors
```bash
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
```

## Success! 🎉

You now have a fully functional AI-powered project management feedback system!

Try submitting different types of feedback:
- Task is too complex → AI suggests breaking it down
- Wrong priorities → AI suggests re-prioritization  
- Missing features → AI suggests new tasks
- Timeline concerns → AI adjusts estimates

The AI analyzes your specific project context and provides actionable suggestions!
