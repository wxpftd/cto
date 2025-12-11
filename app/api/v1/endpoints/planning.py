from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
import json

from app.core.database import get_db
from app.schemas.planning import (
    PlanVersionResponse,
    GeneratePlanRequest,
    DailySummaryResponse,
    GenerateDailyPlanRequest,
    MarkTaskCompleteRequest,
    DailyPlanSummary,
    PlanContent
)
from app.services.planning_service import PlanningService
from app.services.daily_planning_service import DailyPlanningService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=PlanVersionResponse, status_code=201)
async def generate_plan(
    request: GeneratePlanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a project plan with roadmap steps and milestones.
    Can be run automatically after classification or manually triggered.
    """
    try:
        service = PlanningService(db)
        plan_version = await service.generate_project_plan(
            project_id=request.project_id,
            user_id=request.user_id,
            force_regenerate=request.force_regenerate
        )
        
        return PlanVersionResponse.model_validate(plan_version)
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/latest", response_model=PlanVersionResponse)
async def get_latest_plan(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest plan version for a project.
    """
    try:
        service = PlanningService(db)
        plan = await service.get_latest_plan(project_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail="No plan found for this project")
        
        return PlanVersionResponse.model_validate(plan)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/content")
async def get_plan_content(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the parsed content of the latest plan for a project.
    """
    try:
        service = PlanningService(db)
        plan = await service.get_latest_plan(project_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail="No plan found for this project")
        
        content = json.loads(plan.content)
        return content
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid plan content format")
    except Exception as e:
        logger.error(f"Error fetching plan content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily/generate")
async def generate_daily_plan(
    request: GenerateDailyPlanRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate daily plan with top 3 tasks for the user.
    """
    try:
        service = DailyPlanningService(db)
        summaries = await service.generate_daily_plan(
            user_id=request.user_id,
            target_date=request.target_date
        )
        
        return [DailySummaryResponse.model_validate(s) for s in summaries]
    
    except Exception as e:
        logger.error(f"Error generating daily plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily/today/{user_id}")
async def get_today_plan(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get today's plan (top 3 tasks) for a user.
    Automatically generates if it doesn't exist.
    """
    try:
        service = DailyPlanningService(db)
        summaries = await service.get_today_plan(user_id)
        
        return [DailySummaryResponse.model_validate(s) for s in summaries]
    
    except Exception as e:
        logger.error(f"Error fetching today's plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/complete")
async def mark_task_complete(
    request: MarkTaskCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a task as complete and update daily summary.
    """
    try:
        service = DailyPlanningService(db)
        task = await service.mark_task_complete(
            task_id=request.task_id,
            user_id=request.user_id,
            hours_worked=request.hours_worked
        )
        
        return {
            "task_id": task.id,
            "status": task.status,
            "completed_at": task.completed_at
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error marking task complete: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily/summary/{user_id}")
async def get_daily_summary(
    user_id: int,
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary of daily plan for a specific date.
    """
    try:
        from datetime import datetime
        
        if date:
            target_date = datetime.fromisoformat(date)
        else:
            target_date = datetime.now()
        
        service = DailyPlanningService(db)
        summary = await service.get_plan_summary(user_id, target_date)
        
        return summary
    
    except Exception as e:
        logger.error(f"Error fetching daily summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_plan_after_classification(project_id: int, user_id: int):
    """
    Background task to generate plan after inbox classification creates a project.
    """
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            service = PlanningService(db)
            plan = await service.generate_project_plan(
                project_id=project_id,
                user_id=user_id,
                force_regenerate=False
            )
            logger.info(f"Auto-generated plan for project {project_id}: version {plan.version_number}")
        except Exception as e:
            logger.error(f"Failed to auto-generate plan for project {project_id}: {str(e)}")
