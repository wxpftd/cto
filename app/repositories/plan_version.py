from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import PlanVersion
from app.repositories.base import BaseRepository


class PlanVersionRepository(BaseRepository[PlanVersion, dict, dict]):
    """Repository for PlanVersion model"""
    
    def __init__(self, db_session: Session):
        super().__init__(PlanVersion, db_session)
    
    def get_by_project(self, project_id: int) -> List[PlanVersion]:
        """Get plan versions by project"""
        return self.db.query(PlanVersion).filter(PlanVersion.project_id == project_id).all()
    
    def get_by_task(self, task_id: int) -> List[PlanVersion]:
        """Get plan versions by task"""
        return self.db.query(PlanVersion).filter(PlanVersion.task_id == task_id).all()
    
    def get_latest_version_for_project(self, project_id: int) -> Optional[PlanVersion]:
        """Get the latest plan version for a project"""
        return self.db.query(PlanVersion).filter(
            PlanVersion.project_id == project_id
        ).order_by(PlanVersion.version_number.desc()).first()
    
    def get_latest_version_for_task(self, task_id: int) -> Optional[PlanVersion]:
        """Get the latest plan version for a task"""
        return self.db.query(PlanVersion).filter(
            PlanVersion.task_id == task_id
        ).order_by(PlanVersion.version_number.desc()).first()
    
    def get_version_history(self, project_id: Optional[int] = None, task_id: Optional[int] = None) -> List[PlanVersion]:
        """Get version history for a project or task"""
        query = self.db.query(PlanVersion)
        if project_id:
            query = query.filter(PlanVersion.project_id == project_id)
        elif task_id:
            query = query.filter(PlanVersion.task_id == task_id)
        return query.order_by(PlanVersion.version_number.desc()).all()