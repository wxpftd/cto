# 🚀 START HERE

Welcome to the Feedback Loop API! This file will help you get started quickly.

## What is this?

An AI-powered project management system that:
- 📝 Captures user feedback about projects and tasks
- 🤖 Analyzes feedback using GPT-4/GPT-3.5
- 💡 Generates actionable re-planning suggestions
- ⚡ Processes everything asynchronously in the background

## Quick Start (5 minutes)

### Step 1: Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it (starts with `sk-`)

### Step 2: Configure

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any text editor
```

Find this line and replace with your actual key:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### Step 3: Start Everything

```bash
# Start all services (PostgreSQL, Redis, API, Worker)
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head
```

### Step 4: Verify It's Running

Open your browser to: **http://localhost:8000/docs**

You should see the interactive API documentation! 🎉

### Step 5: Try It Out!

#### Option A: Use the Swagger UI
1. Go to http://localhost:8000/docs
2. Expand `POST /projects/` and click "Try it out"
3. Create a project, then tasks, then submit feedback
4. Watch AI generate suggestions!

#### Option B: Run the Test Script
```bash
./scripts/test_workflow.sh
```

This automated script will:
- Create a project
- Add tasks
- Submit feedback
- Wait for AI processing
- Show you the results!

## 📚 What to Read Next

Depending on what you want to do:

### I want to understand the system
→ Read [ARCHITECTURE.md](ARCHITECTURE.md)

### I want detailed setup instructions
→ Read [README.md](README.md)

### I want to see API examples
→ Check [examples/README.md](examples/README.md)

### I want complete API documentation
→ Read [API_REFERENCE.md](API_REFERENCE.md)

### I want to know what was built
→ Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## 🎯 Your First Workflow

Here's what a typical usage looks like:

```bash
# 1. Create a project
curl -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "A test project"}'
# Returns: {"id": 1, ...}

# 2. Create a task
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Build complex feature",
    "status": "in_progress",
    "priority": 5
  }'
# Returns: {"id": 1, ...}

# 3. Submit feedback (triggers AI)
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "task_id": 1,
    "user_name": "John",
    "feedback_text": "This task is too big. We should split it into smaller pieces."
  }'
# Returns: {"feedback_id": 1, "status": "pending", ...}

# 4. Wait ~15 seconds for AI processing...

# 5. Get AI suggestions
curl http://localhost:8000/feedback/1
# Returns feedback with AI-generated adjustments!
```

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f

# View API logs specifically
docker-compose logs -f api

# View worker logs (see AI processing!)
docker-compose logs -f celery_worker

# Restart services
docker-compose restart

# Stop everything
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## ❓ Troubleshooting

### "Connection refused" when accessing API
```bash
# Check if services are running
docker-compose ps

# If not, start them
docker-compose up -d
```

### Feedback stuck in "pending" status
```bash
# Check worker logs
docker-compose logs celery_worker

# Common issues:
# - Invalid OpenAI API key (check .env)
# - No credits in OpenAI account
# - Worker not running
```

### Can't access database
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check if it's healthy
docker-compose ps postgres
```

## 📖 Documentation Overview

| File | Purpose | When to Read |
|------|---------|--------------|
| **START_HERE.md** | You are here! | First |
| **QUICKSTART.md** | 5-minute setup guide | Getting started |
| **README.md** | Main documentation | Detailed setup |
| **API_REFERENCE.md** | Complete API docs | Using the API |
| **ARCHITECTURE.md** | System design | Understanding internals |
| **PROJECT_SUMMARY.md** | What was built | Overview |
| **examples/README.md** | Usage examples | Learning by example |

## 🎓 Key Concepts

**Project** → Container for related tasks
**Task** → Individual work item
**Feedback** → User input about project/task
**Adjustment** → AI-generated suggestion based on feedback

**Flow:**
```
User Feedback → Background Worker → AI Analysis → Adjustments → You Apply
```

## 💡 Tips

1. **Start with the test script** - It shows the complete workflow
2. **Use Swagger UI** - Great for exploration and testing
3. **Check worker logs** - See AI processing in real-time
4. **Try different feedback** - See how AI responds differently
5. **Read the examples** - Learn from real scenarios

## 🚀 Next Steps

1. ✅ Get OpenAI API key
2. ✅ Configure `.env` file
3. ✅ Start services with Docker Compose
4. ✅ Run migrations
5. ✅ Visit http://localhost:8000/docs
6. ✅ Run test script OR create project manually
7. ✅ Submit feedback and watch AI work!

## 🎉 You're Ready!

The system is production-ready and includes:
- ✅ Complete API with documentation
- ✅ AI-powered re-planning
- ✅ Background processing
- ✅ Database with migrations
- ✅ Docker setup
- ✅ Example workflows
- ✅ Comprehensive documentation

**Have questions?** Check the detailed docs in the links above!

**Ready to dive in?** Run `./scripts/test_workflow.sh` and watch the magic happen! ✨
