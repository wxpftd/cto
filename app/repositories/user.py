from sqlalchemy.orm import Session
from typing import Optional
from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, dict, dict]):
    """Repository for User model"""
    
    def __init__(self, db_session: Session):
        super().__init__(User, db_session)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_active_users(self) -> list[User]:
        """Get all active users"""
        return self.db.query(User).filter(User.is_active == True).all()