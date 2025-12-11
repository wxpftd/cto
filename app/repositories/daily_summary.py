from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from app.models import DailySummary
from app.repositories.base import BaseRepository


class DailySummaryRepository(BaseRepository[DailySummary, dict, dict]):
    """Repository for DailySummary model"""
    
    def __init__(self, db_session: Session):
        super().__init__(DailySummary, db_session)
    
    def get_by_date(self, date: datetime) -> List[DailySummary]:
        """Get daily summaries by date"""
        # Get summaries for the specific date (ignoring time)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return self.db.query(DailySummary).filter(
            DailySummary.date >= start_of_day,
            DailySummary.date <= end_of_day
        ).all()
    
    def get_by_user(self, user_id: int) -> List[DailySummary]:
        """Get daily summaries by user"""
        return self.db.query(DailySummary).filter(DailySummary.user_id == user_id).all()
    
    def get_by_task(self, task_id: int) -> List[DailySummary]:
        """Get daily summaries by task"""
        return self.db.query(DailySummary).filter(DailySummary.task_id == task_id).all()
    
    def get_recent_summaries(self, user_id: int, days: int = 7) -> List[DailySummary]:
        """Get recent daily summaries for a user"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(DailySummary).filter(
            DailySummary.user_id == user_id,
            DailySummary.date >= cutoff_date
        ).order_by(DailySummary.date.desc()).all()