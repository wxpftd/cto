from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class PlanVersionResponse(BaseModel):
    id: int
    version_number: int
    content: str
    project_id: Optional[int]
    task_id: Optional[int]
    created_by: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GeneratePlanRequest(BaseModel):
    project_id: int
    user_id: int
    force_regenerate: bool = False


class RoadmapStep(BaseModel):
    step_number: int
    title: str
    description: str
    estimated_duration: str
    dependencies: List[int] = []


class Milestone(BaseModel):
    title: str
    target_date: str
    deliverables: List[str]


class PlanContent(BaseModel):
    summary: str
    goals: List[str]
    roadmap_steps: List[RoadmapStep]
    milestones: List[Milestone]
    risks: List[str] = []
    next_steps: List[str]


class DailySummaryResponse(BaseModel):
    id: int
    date: datetime
    summary_text: str
    user_id: int
    task_id: Optional[int]
    tasks_completed: int
    hours_worked: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GenerateDailyPlanRequest(BaseModel):
    user_id: int
    target_date: Optional[datetime] = None


class MarkTaskCompleteRequest(BaseModel):
    task_id: int
    user_id: int
    hours_worked: Optional[int] = None


class DailyPlanSummary(BaseModel):
    date: str
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    total_hours_worked: int
    summaries: List[Dict[str, Any]]
