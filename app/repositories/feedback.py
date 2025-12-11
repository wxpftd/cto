from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Feedback
from app.repositories.base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback, dict, dict]):
    """Repository for Feedback model"""
    
    def __init__(self, db_session: Session):
        super().__init__(Feedback, db_session)
    
    def get_by_type(self, feedback_type: str) -> List[Feedback]:
        """Get feedback by type"""
        return self.db.query(Feedback).filter(Feedback.feedback_type == feedback_type).all()
    
    def get_by_project(self, project_id: int) -> List[Feedback]:
        """Get feedback by project"""
        return self.db.query(Feedback).filter(Feedback.project_id == project_id).all()
    
    def get_by_task(self, task_id: int) -> List[Feedback]:
        """Get feedback by task"""
        return self.db.query(Feedback).filter(Feedback.task_id == task_id).all()
    
    def get_unresolved_feedback(self) -> List[Feedback]:
        """Get unresolved feedback"""
        return self.db.query(Feedback).filter(Feedback.is_resolved == False).all()
    
    def get_by_user(self, user_id: int) -> List[Feedback]:
        """Get feedback by user"""
        return self.db.query(Feedback).filter(Feedback.user_id == user_id).all()