from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.core.database import get_db
from app.schemas.inbox import InboxItemCreate, InboxItemResponse
from app.services.inbox_service import InboxService
from app.models import InboxItem

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=InboxItemResponse, status_code=201)
async def create_inbox_item(
    item: InboxItemCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new inbox item and trigger async LLM classification in the background.
    """
    try:
        service = InboxService(db)
        inbox_item = await service.create_inbox_item(
            content=item.content,
            user_id=item.user_id,
            tags=item.tags
        )
        
        background_tasks.add_task(
            process_inbox_item_background,
            inbox_item.id,
            item.user_id
        )
        
        return InboxItemResponse.model_validate(inbox_item)
    
    except Exception as e:
        logger.error(f"Error creating inbox item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{inbox_item_id}/process")
async def process_inbox_item_sync(
    inbox_item_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Synchronously process an inbox item with LLM classification.
    """
    try:
        service = InboxService(db)
        result = await service.process_inbox_item(inbox_item_id, user_id)
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing inbox item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{inbox_item_id}", response_model=InboxItemResponse)
async def get_inbox_item(
    inbox_item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific inbox item by ID.
    """
    result = await db.get(InboxItem, inbox_item_id)
    if not result:
        raise HTTPException(status_code=404, detail="InboxItem not found")
    
    return InboxItemResponse.model_validate(result)


async def process_inbox_item_background(inbox_item_id: int, user_id: int):
    """
    Background task to process inbox item with LLM classification.
    This creates a new database session for the background task.
    """
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            service = InboxService(db)
            result = await service.process_inbox_item(inbox_item_id, user_id)
            logger.info(f"Background processing completed for inbox item {inbox_item_id}: {result}")
        except Exception as e:
            logger.error(f"Background processing failed for inbox item {inbox_item_id}: {str(e)}")
