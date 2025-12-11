import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.models import Task, DailySummary, User

logger = logging.getLogger(__name__)


class DailyPlanningService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    PRIORITY_SCORES = {
        'urgent': 4,
        'high': 3,
        'medium': 2,
        'low': 1
    }
    
    async def generate_daily_plan(
        self,
        user_id: int,
        target_date: Optional[datetime] = None
    ) -> List[DailySummary]:
        if target_date is None:
            target_date = datetime.now()
        
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        result = await self.db.execute(
            select(DailySummary).filter(
                and_(
                    DailySummary.user_id == user_id,
                    DailySummary.date >= start_of_day,
                    DailySummary.date <= end_of_day
                )
            )
        )
        existing_summaries = result.scalars().all()
        
        if existing_summaries:
            logger.info(f"Daily plan already exists for user {user_id} on {target_date.date()}")
            return list(existing_summaries)
        
        top_tasks = await self._select_top_three_tasks(user_id, target_date)
        
        summaries = []
        for idx, task in enumerate(top_tasks, 1):
            summary_text = self._generate_summary_text(task, idx)
            
            daily_summary = DailySummary(
                date=start_of_day,
                summary_text=summary_text,
                user_id=user_id,
                task_id=task.id,
                tasks_completed=0,
                hours_worked=0
            )
            self.db.add(daily_summary)
            summaries.append(daily_summary)
        
        if summaries:
            await self.db.commit()
            for summary in summaries:
                await self.db.refresh(summary)
            logger.info(f"Generated daily plan with {len(summaries)} tasks for user {user_id}")
        else:
            logger.info(f"No tasks available for daily plan for user {user_id}")
        
        return summaries
    
    async def _select_top_three_tasks(
        self,
        user_id: int,
        target_date: datetime
    ) -> List[Task]:
        result = await self.db.execute(
            select(Task).filter(
                and_(
                    Task.assignee_id == user_id,
                    or_(
                        Task.status == 'pending',
                        Task.status == 'in_progress'
                    )
                )
            )
        )
        candidate_tasks = result.scalars().all()
        
        if not candidate_tasks:
            return []
        
        scored_tasks = []
        for task in candidate_tasks:
            score = self._calculate_task_score(task, target_date)
            scored_tasks.append((score, task))
        
        scored_tasks.sort(key=lambda x: x[0], reverse=True)
        
        top_three = [task for score, task in scored_tasks[:3]]
        
        return top_three
    
    def _calculate_task_score(self, task: Task, reference_date: datetime) -> float:
        score = 0.0
        
        base_priority_score = self.PRIORITY_SCORES.get(task.priority, 1)
        score += base_priority_score * 10
        
        if task.status == 'in_progress':
            score += 15
        
        if task.due_date:
            days_until_due = (task.due_date - reference_date).days
            
            if days_until_due < 0:
                score += 50
            elif days_until_due == 0:
                score += 40
            elif days_until_due <= 3:
                score += 30
            elif days_until_due <= 7:
                score += 20
            elif days_until_due <= 14:
                score += 10
        
        if task.created_at:
            days_since_creation = (reference_date - task.created_at).days
            if days_since_creation > 30:
                score += 5
        
        return score
    
    def _generate_summary_text(self, task: Task, rank: int) -> str:
        priority_emoji = {
            'urgent': '🔥',
            'high': '⚡',
            'medium': '📌',
            'low': '💡'
        }
        
        emoji = priority_emoji.get(task.priority, '📌')
        
        due_info = ""
        if task.due_date:
            days_until_due = (task.due_date - datetime.now()).days
            if days_until_due < 0:
                due_info = f" (OVERDUE by {abs(days_until_due)} days)"
            elif days_until_due == 0:
                due_info = " (DUE TODAY)"
            elif days_until_due <= 3:
                due_info = f" (Due in {days_until_due} days)"
        
        return f"#{rank} {emoji} {task.title}{due_info}"
    
    async def get_today_plan(self, user_id: int) -> List[DailySummary]:
        today = datetime.now()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        result = await self.db.execute(
            select(DailySummary).filter(
                and_(
                    DailySummary.user_id == user_id,
                    DailySummary.date >= start_of_day,
                    DailySummary.date <= end_of_day
                )
            )
        )
        summaries = result.scalars().all()
        
        if not summaries:
            summaries = await self.generate_daily_plan(user_id, today)
        
        return list(summaries)
    
    async def mark_task_complete(
        self,
        task_id: int,
        user_id: int,
        hours_worked: Optional[int] = None
    ) -> Task:
        result = await self.db.get(Task, task_id)
        if not result:
            raise ValueError(f"Task {task_id} not found")
        
        task = result
        
        if task.assignee_id != user_id:
            raise ValueError(f"Task {task_id} is not assigned to user {user_id}")
        
        task.status = 'completed'
        task.completed_at = datetime.now()
        
        today = datetime.now()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        result = await self.db.execute(
            select(DailySummary).filter(
                and_(
                    DailySummary.user_id == user_id,
                    DailySummary.task_id == task_id,
                    DailySummary.date >= start_of_day,
                    DailySummary.date <= end_of_day
                )
            )
        )
        daily_summary = result.scalar_one_or_none()
        
        if daily_summary:
            daily_summary.tasks_completed = 1
            if hours_worked is not None:
                daily_summary.hours_worked = hours_worked
            
            summary_parts = daily_summary.summary_text.split(' - ')
            if len(summary_parts) == 1:
                daily_summary.summary_text = f"{summary_parts[0]} - ✅ COMPLETED"
            else:
                daily_summary.summary_text = f"{summary_parts[0]} - ✅ COMPLETED"
        
        await self.db.commit()
        await self.db.refresh(task)
        
        logger.info(f"Marked task {task_id} as complete for user {user_id}")
        return task
    
    async def get_plan_summary(self, user_id: int, date: datetime) -> Dict[str, Any]:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        result = await self.db.execute(
            select(DailySummary).filter(
                and_(
                    DailySummary.user_id == user_id,
                    DailySummary.date >= start_of_day,
                    DailySummary.date <= end_of_day
                )
            )
        )
        summaries = result.scalars().all()
        
        total_tasks = len(summaries)
        completed_tasks = sum(1 for s in summaries if s.tasks_completed > 0)
        total_hours = sum(s.hours_worked for s in summaries)
        
        return {
            "date": date.date().isoformat(),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_hours_worked": total_hours,
            "summaries": [
                {
                    "id": s.id,
                    "summary_text": s.summary_text,
                    "task_id": s.task_id,
                    "completed": s.tasks_completed > 0,
                    "hours_worked": s.hours_worked
                }
                for s in summaries
            ]
        }
