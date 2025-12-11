from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import LlmCallLog
from app.repositories.base import BaseRepository


class LlmCallLogRepository(BaseRepository[LlmCallLog, dict, dict]):
    """Repository for LlmCallLog model"""
    
    def __init__(self, db_session: Session):
        super().__init__(LlmCallLog, db_session)
    
    def get_by_user(self, user_id: int) -> List[LlmCallLog]:
        """Get LLM call logs by user"""
        return self.db.query(LlmCallLog).filter(LlmCallLog.user_id == user_id).all()
    
    def get_by_model(self, model_name: str) -> List[LlmCallLog]:
        """Get LLM call logs by model"""
        return self.db.query(LlmCallLog).filter(LlmCallLog.model_name == model_name).all()
    
    def get_successful_calls(self) -> List[LlmCallLog]:
        """Get successful LLM calls"""
        return self.db.query(LlmCallLog).filter(LlmCallLog.status == 'success').all()
    
    def get_failed_calls(self) -> List[LlmCallLog]:
        """Get failed LLM calls"""
        return self.db.query(LlmCallLog).filter(LlmCallLog.status == 'error').all()
    
    def get_recent_calls(self, user_id: int, limit: int = 10) -> List[LlmCallLog]:
        """Get recent LLM calls for a user"""
        return self.db.query(LlmCallLog).filter(
            LlmCallLog.user_id == user_id
        ).order_by(LlmCallLog.created_at.desc()).limit(limit).all()