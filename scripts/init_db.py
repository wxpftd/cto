#!/usr/bin/env python3
"""
Database initialization script.
Creates initial data for testing and development.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Project, Task, ProjectStatus, TaskStatus


def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing_project = db.query(Project).first()
        if existing_project:
            print("Database already has data. Skipping initialization.")
            return
        
        print("Creating sample project...")
        project = Project(
            name="Sample Project",
            description="A sample project to get you started",
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.flush()
        
        print("Creating sample tasks...")
        tasks = [
            Task(
                project_id=project.id,
                title="Setup project infrastructure",
                description="Configure CI/CD, development environment",
                status=TaskStatus.COMPLETED,
                priority=10,
                estimated_hours=20
            ),
            Task(
                project_id=project.id,
                title="Implement core features",
                description="Build the main functionality",
                status=TaskStatus.IN_PROGRESS,
                priority=8,
                estimated_hours=80
            ),
            Task(
                project_id=project.id,
                title="Write documentation",
                description="Create user and developer documentation",
                status=TaskStatus.TODO,
                priority=5,
                estimated_hours=30
            ),
        ]
        
        for task in tasks:
            db.add(task)
        
        db.commit()
        print(f"✓ Created project (ID: {project.id}) with {len(tasks)} tasks")
        print("\nYou can now:")
        print(f"1. View the project: curl http://localhost:8000/projects/{project.id}")
        print(f"2. Submit feedback: curl -X POST http://localhost:8000/feedback/ -d '{...}'")
        print("3. Access API docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
