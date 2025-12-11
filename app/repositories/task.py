from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task, dict, dict]):
    """Repository for Task model"""
    
    def __init__(self, db_session: Session):
        super().__init__(Task, db_session)
    
    def get_by_project(self, project_id: int) -> List[Task]:
        """Get tasks by project"""
        return self.db.query(Task).filter(Task.project_id == project_id).all()
    
    def get_by_assignee(self, assignee_id: int) -> List[Task]:
        """Get tasks by assignee"""
        return self.db.query(Task).filter(Task.assignee_id == assignee_id).all()
    
    def get_by_status(self, status: str) -> List[Task]:
        """Get tasks by status"""
        return self.db.query(Task).filter(Task.status == status).all()
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        from datetime import datetime
        return self.db.query(Task).filter(
            Task.due_date < datetime.utcnow(),
            Task.status != 'completed'
        ).all()
    
    def get_pending_tasks(self) -> List[Task]:
        """Get pending tasks"""
        return self.db.query(Task).filter(Task.status == 'pending').all()