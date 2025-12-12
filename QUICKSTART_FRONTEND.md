# Quick Start - Frontend Integration

The Feedback Loop now includes a complete React + TypeScript frontend! 🎉

## 🚀 Fastest Way to Get Started

### Using Docker (Recommended - One Command)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 2. Start everything with one command
make docker-up

# 3. Open in browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

That's it! All services will start automatically (Frontend, API, Database, Workers).

---

## 🛠️ Development Setup (Multiple Terminals)

### Terminal 1 - Backend Setup

```bash
# Install and setup backend
make install
make setup

# Start API server
make dev
```

### Terminal 2 - Background Worker

```bash
# Start Celery worker (for AI processing)
make worker
```

### Terminal 3 - Frontend Server

```bash
# Install frontend dependencies
make frontend-install

# Start frontend dev server
make frontend-dev
```

Then open: **http://localhost:5173**

---

## 📖 Documentation

- **Complete Frontend Guide**: [frontend/README.md](frontend/README.md)
- **Integration Details**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Integration Summary**: [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)

---

## 🎯 What You Can Do

### In the Frontend

✅ Create and manage projects
✅ Add tasks with priority and status tracking
✅ Submit feedback for projects or specific tasks
✅ View real-time AI suggestions generated from your feedback
✅ Edit and delete projects and tasks
✅ Track feedback processing status

### Try This Workflow

1. **Create a Project**
   - Click "New Project" button
   - Fill in project name and description
   - Save

2. **Add Some Tasks**
   - Go to project detail
   - Click "Add Task" 
   - Create a few tasks with different priorities

3. **Submit Feedback**
   - Go to "Feedback" tab
   - Click "Add Feedback"
   - Write something like: "Task 1 is taking too long, we should break it down"
   - Submit

4. **Watch AI Process Your Feedback**
   - Status changes from "pending" to "processing"
   - Once complete, you'll see AI-generated suggestions!

---

## 🐛 Troubleshooting

### Frontend can't connect to backend

```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend .env
cat frontend/.env
# Should have: VITE_API_URL=http://localhost:8000
```

### Docker container issues

```bash
# View logs
make docker-logs

# Restart everything
make docker-down
make docker-up
```

### Database errors

```bash
# Reset everything
docker-compose down -v
docker-compose up -d
make docker-migrate
```

---

## 📁 Project Structure

```
feedback-loop/
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── app/                     # Python Backend
├── docker-compose.yml       # All services
├── Makefile                 # Helper commands
└── README.md                # Main docs
```

---

## 🔧 Available Commands

```bash
# Frontend only
make frontend-install   # Install npm packages
make frontend-dev      # Start dev server

# Backend only
make install           # Install Python packages
make setup            # Setup database
make dev              # Start API server
make worker           # Start Celery worker

# Everything together
make docker-up        # Start all with Docker
make docker-down      # Stop all
make docker-logs      # View logs
```

---

## 🌐 URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | React app |
| API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | API documentation |
| Redis | localhost:6379 | Message broker |
| PostgreSQL | localhost:5432 | Database |

---

## ✨ Next Steps

- Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for architecture details
- Check [API_REFERENCE.md](API_REFERENCE.md) for all endpoints
- Explore `frontend/src/` to understand the code
- Try the API docs at http://localhost:8000/docs

---

## 🆘 Need Help?

1. **Check Documentation**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. **View Logs**: `make docker-logs`
3. **Test API**: http://localhost:8000/docs
4. **Check Frontend**: `frontend/README.md`

---

**Ready? Start with `make docker-up` and open http://localhost:5173!** 🚀
