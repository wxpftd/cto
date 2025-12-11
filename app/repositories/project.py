from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project, dict, dict]):
    """Repository for Project model"""
    
    def __init__(self, db_session: Session):
        super().__init__(Project, db_session)
    
    def get_by_owner(self, owner_id: int) -> List[Project]:
        """Get projects by owner"""
        return self.db.query(Project).filter(Project.owner_id == owner_id).all()
    
    def get_by_status(self, status: str) -> List[Project]:
        """Get projects by status"""
        return self.db.query(Project).filter(Project.status == status).all()
    
    def get_active_projects_by_owner(self, owner_id: int) -> List[Project]:
        """Get active projects for a specific owner"""
        return self.db.query(Project).filter(
            Project.owner_id == owner_id,
            Project.status == 'active'
        ).all()