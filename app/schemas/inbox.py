from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InboxItemCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Content of the inbox item")
    user_id: int = Field(..., description="User ID who created the item")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags")


class InboxItemResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    content: str
    user_id: int
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    status: str
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class ClassificationAction(str, Enum):
    CREATE_PROJECT = "create_project"
    CREATE_TASK = "create_task"
    ATTACH_TO_EXISTING = "attach_to_existing"
    NO_ACTION = "no_action"


class InboxItemClassification(BaseModel):
    action: ClassificationAction
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    task_title: Optional[str] = None
    task_description: Optional[str] = None
    task_priority: Optional[str] = None
    suggested_project_id: Optional[int] = None
    suggested_task_id: Optional[int] = None
    reasoning: Optional[str] = None
