from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import ProjectStatus, TaskStatus, FeedbackStatus


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: int = Field(default=0, ge=0, le=10)
    estimated_hours: Optional[float] = Field(None, gt=0)


class TaskCreate(TaskBase):
    project_id: int = Field(..., description="Project ID this task belongs to")


class Task(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackBase(BaseModel):
    project_id: int = Field(..., description="Project ID for the feedback")
    task_id: Optional[int] = Field(None, description="Optional Task ID if feedback is task-specific")
    user_name: Optional[str] = Field(None, max_length=255, description="Name of the user providing feedback")
    feedback_text: str = Field(..., min_length=1, description="The actual feedback content")


class FeedbackCreate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: int
    status: FeedbackStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdjustmentBase(BaseModel):
    adjustment_type: str = Field(..., description="Type of adjustment (e.g., 'task_priority', 'task_description', 'new_task')")
    description: str = Field(..., description="Description of the adjustment")
    original_value: Optional[str] = Field(None, description="Original value before adjustment")
    new_value: Optional[str] = Field(None, description="New value after adjustment")
    reasoning: Optional[str] = Field(None, description="LLM's reasoning for this adjustment")


class Adjustment(AdjustmentBase):
    id: int
    feedback_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackWithAdjustments(Feedback):
    adjustments: List[Adjustment] = []


class ProjectWithTasks(Project):
    tasks: List[Task] = []


class FeedbackResponse(BaseModel):
    feedback_id: int
    status: FeedbackStatus
    message: str
    task_id: Optional[str] = None


class ReplanningResult(BaseModel):
    feedback_id: int
    adjustments: List[Adjustment]
    summary: str
