from sqlalchemy.orm import Session
from typing import List, Optional, Type, TypeVar, Generic
from app.models import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db_session: Session):
        self.model = model
        self.db = db_session

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        """Get all records with optional pagination"""
        return self.db.query(self.model).offset(offset).limit(limit).all()

    def create(self, data: CreateSchemaType) -> ModelType:
        """Create a new record"""
        db_record = self.model(**data.dict() if hasattr(data, 'dict') else data)
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(self, id: int, data: UpdateSchemaType) -> Optional[ModelType]:
        """Update a record"""
        db_record = self.get_by_id(id)
        if db_record:
            update_data = data.dict() if hasattr(data, 'dict') else data
            for field, value in update_data.items():
                if hasattr(db_record, field):
                    setattr(db_record, field, value)
            self.db.commit()
            self.db.refresh(db_record)
        return db_record

    def delete(self, id: int) -> bool:
        """Delete a record"""
        db_record = self.get_by_id(id)
        if db_record:
            self.db.delete(db_record)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """Count total records"""
        return self.db.query(self.model).count()