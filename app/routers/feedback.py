from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Feedback, Project, Task, FeedbackStatus
from app.schemas import (
    FeedbackCreate, Feedback as FeedbackSchema,
    FeedbackResponse, FeedbackWithAdjustments
)
from app.workers.tasks import process_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback: FeedbackCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit user feedback for a project or task.
    
    This endpoint captures user feedback and triggers an asynchronous re-planning workflow.
    The LLM will analyze the feedback in the context of the project and tasks, then suggest
    adjustments such as:
    - Changing task priorities
    - Modifying task descriptions
    - Adding new tasks
    - Changing task statuses
    - Removing or consolidating tasks
    
    **Example Request:**
    ```json
    {
        "project_id": 1,
        "task_id": 5,
        "user_name": "John Doe",
        "feedback_text": "This task is taking too long. We need to break it into smaller pieces and prioritize the critical features first."
    }
    ```
    
    **Response:**
    The endpoint returns immediately with a feedback ID and status. The actual processing
    happens asynchronously in the background.
    """
    project = db.query(Project).filter(Project.id == feedback.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if feedback.task_id:
        task = db.query(Task).filter(Task.id == feedback.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.project_id != feedback.project_id:
            raise HTTPException(
                status_code=400,
                detail="Task does not belong to the specified project"
            )
    
    db_feedback = Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    task_result = process_feedback.apply_async(args=[db_feedback.id])
    
    return FeedbackResponse(
        feedback_id=db_feedback.id,
        status=db_feedback.status,
        message="Feedback received and queued for processing",
        task_id=str(task_result.id)
    )


@router.get("/", response_model=List[FeedbackSchema])
def list_feedback(
    project_id: int = None,
    task_id: int = None,
    status: FeedbackStatus = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List feedback entries with optional filters.
    
    **Query Parameters:**
    - project_id: Filter by project
    - task_id: Filter by task
    - status: Filter by feedback status (pending, processing, completed, failed)
    - skip: Pagination offset
    - limit: Maximum number of results
    """
    query = db.query(Feedback)
    
    if project_id:
        query = query.filter(Feedback.project_id == project_id)
    if task_id:
        query = query.filter(Feedback.task_id == task_id)
    if status:
        query = query.filter(Feedback.status == status)
    
    feedbacks = query.offset(skip).limit(limit).all()
    return feedbacks


@router.get("/{feedback_id}", response_model=FeedbackWithAdjustments)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed feedback information including all generated adjustments.
    
    **Example Response:**
    ```json
    {
        "id": 1,
        "project_id": 1,
        "task_id": 5,
        "user_name": "John Doe",
        "feedback_text": "This task is taking too long...",
        "status": "completed",
        "created_at": "2024-01-15T10:30:00",
        "processed_at": "2024-01-15T10:31:23",
        "adjustments": [
            {
                "id": 1,
                "adjustment_type": "task_priority",
                "description": "Increase priority of critical features",
                "original_value": "3",
                "new_value": "8",
                "reasoning": "Based on feedback, critical features should be prioritized",
                "feedback_id": 1,
                "created_at": "2024-01-15T10:31:23"
            }
        ]
    }
    ```
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a feedback entry and all associated adjustments.
    """
    db_feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    db.delete(db_feedback)
    db.commit()
    return None
