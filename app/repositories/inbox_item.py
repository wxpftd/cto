from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import InboxItem
from app.repositories.base import BaseRepository


class InboxItemRepository(BaseRepository[InboxItem, dict, dict]):
    """Repository for InboxItem model"""
    
    def __init__(self, db_session: Session):
        super().__init__(InboxItem, db_session)
    
    def get_by_user(self, user_id: int) -> List[InboxItem]:
        """Get inbox items by user"""
        return self.db.query(InboxItem).filter(InboxItem.user_id == user_id).all()
    
    def get_by_status(self, status: str) -> List[InboxItem]:
        """Get inbox items by status"""
        return self.db.query(InboxItem).filter(InboxItem.status == status).all()
    
    def get_by_project(self, project_id: int) -> List[InboxItem]:
        """Get inbox items by project"""
        return self.db.query(InboxItem).filter(InboxItem.project_id == project_id).all()
    
    def get_unprocessed_by_user(self, user_id: int) -> List[InboxItem]:
        """Get unprocessed inbox items for a user"""
        return self.db.query(InboxItem).filter(
            InboxItem.user_id == user_id,
            InboxItem.status == 'unprocessed'
        ).all()