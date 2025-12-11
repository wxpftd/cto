from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class User(Base):
    """User model for authentication and ownership"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="assignee")
    inbox_items = relationship("InboxItem", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Project model for organizing tasks and plans"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum('active', 'completed', 'archived', name='project_status'), default='active')
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects", foreign_keys="Project.owner_id")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    inbox_items = relationship("InboxItem", back_populates="project")
    plan_versions = relationship("PlanVersion", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    """Task model for specific work items"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum('pending', 'in_progress', 'completed', 'cancelled', name='task_status'), default='pending')
    priority = Column(Enum('low', 'medium', 'high', 'urgent', name='task_priority'), default='medium')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    assignee_id = Column(Integer, ForeignKey('users.id'))
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks", foreign_keys="Task.assignee_id")
    inbox_items = relationship("InboxItem", back_populates="task")
    plan_versions = relationship("PlanVersion", back_populates="task")
    daily_summaries = relationship("DailySummary", back_populates="task")


class InboxItem(Base):
    """InboxItem for capturing ideas/tasks before they're organized"""
    __tablename__ = 'inbox_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    status = Column(Enum('unprocessed', 'processed', 'archived', name='inbox_status'), default='unprocessed')
    tags = Column(JSON)  # Store tags as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="inbox_items")
    project = relationship("Project", back_populates="inbox_items")
    task = relationship("Task", back_populates="inbox_items")


class PlanVersion(Base):
    """PlanVersion for tracking project/task plan evolution"""
    __tablename__ = 'plan_versions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)  # JSON or markdown content
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="plan_versions")
    task = relationship("Task", back_populates="plan_versions", foreign_keys="PlanVersion.task_id")
    creator = relationship("User", foreign_keys="PlanVersion.created_by")


class Feedback(Base):
    """Feedback model for capturing user/system feedback"""
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    feedback_type = Column(Enum('user_input', 'system_output', 'improvement', name='feedback_type'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    plan_version_id = Column(Integer, ForeignKey('plan_versions.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer)  # 1-5 scale if applicable
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project")
    task = relationship("Task")
    plan_version = relationship("PlanVersion")
    user = relationship("User")


class DailySummary(Base):
    """DailySummary for tracking daily task progress"""
    __tablename__ = 'daily_summaries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime(timezone=True), nullable=False)
    summary_text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    tasks_completed = Column(Integer, default=0)
    hours_worked = Column(Integer, default=0)  # Store in minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    task = relationship("Task", back_populates="daily_summaries")


class LlmCallLog(Base):
    """LlmCallLog for tracking AI/LLM API calls"""
    __tablename__ = 'llm_call_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    model_name = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    tokens_used = Column(Integer)
    cost_usd = Column(Integer, default=0)  # Store in cents
    execution_time_ms = Column(Integer)
    status = Column(Enum('success', 'error', 'timeout', name='llm_call_status'), default='success')
    error_message = Column(Text)
    extra_metadata = Column(JSON)  # Additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")