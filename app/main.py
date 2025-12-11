from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import projects, tasks, feedback

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Feedback Loop API

An intelligent project management system that captures user feedback and automatically 
generates re-planning suggestions using LLM analysis.

### Features

* 📋 **Project Management**: Create and manage projects with tasks
* 💬 **Feedback Capture**: Submit feedback linked to projects or specific tasks
* 🤖 **AI-Powered Re-planning**: Automatic analysis and adjustment suggestions via LLM
* ⚡ **Async Processing**: Background workers handle LLM processing
* 📊 **Adjustment Tracking**: Store and retrieve all suggested changes

### Workflow

1. **Create a project** with tasks
2. **Submit feedback** via the feedback endpoint
3. **Background worker** analyzes feedback using LLM
4. **Retrieve adjustments** to see suggested changes
5. **Apply changes** to your project plan

### Example Use Cases

- User reports a task is taking too long → LLM suggests breaking it into smaller tasks
- Stakeholder requests feature prioritization → LLM adjusts task priorities
- Team member identifies blockers → LLM suggests task reordering or status changes
- Customer feedback requires scope change → LLM suggests new tasks or modifications
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(feedback.router)


@app.get("/", tags=["Health"])
def read_root():
    return {
        "message": "Feedback Loop API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
