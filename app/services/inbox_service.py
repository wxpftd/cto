import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.llm import get_llm_client
from app.schemas.inbox import InboxItemClassification, ClassificationAction
from app.models import InboxItem, Project, Task, LlmCallLog, User
from app.core.config import settings

logger = logging.getLogger(__name__)


class InboxService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_inbox_item(self, content: str, user_id: int, tags: Optional[list] = None) -> InboxItem:
        inbox_item = InboxItem(
            content=content,
            user_id=user_id,
            tags=tags,
            status="unprocessed"
        )
        self.db.add(inbox_item)
        await self.db.commit()
        await self.db.refresh(inbox_item)
        return inbox_item
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    async def classify_with_llm(self, content: str, user_id: int) -> InboxItemClassification:
        start_time = datetime.now()
        llm_client = get_llm_client()
        
        prompt = self._build_classification_prompt(content)
        
        try:
            response = await llm_client.complete(prompt, temperature=0.3, max_tokens=500)
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            classification = self._parse_classification_response(response.content)
            
            await self._log_llm_call(
                user_id=user_id,
                model_name=response.model,
                prompt=prompt,
                response=response.content,
                tokens_used=response.tokens_used,
                execution_time_ms=execution_time_ms,
                status="success",
                metadata=response.metadata
            )
            
            return classification
            
        except Exception as e:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            await self._log_llm_call(
                user_id=user_id,
                model_name=settings.LLM_MODEL,
                prompt=prompt,
                response=None,
                tokens_used=None,
                execution_time_ms=execution_time_ms,
                status="error",
                error_message=str(e)
            )
            logger.error(f"LLM classification failed: {str(e)}")
            raise
    
    def _build_classification_prompt(self, content: str) -> str:
        return f"""Analyze the following inbox item and determine the best action to take.

Inbox item: "{content}"

Respond with a JSON object with the following structure:
{{
    "action": "create_project" | "create_task" | "attach_to_existing" | "no_action",
    "project_name": "optional project name if action is create_project",
    "project_description": "optional project description",
    "task_title": "optional task title if action is create_task",
    "task_description": "optional task description",
    "task_priority": "low" | "medium" | "high" | "urgent",
    "reasoning": "brief explanation of your decision"
}}

Guidelines:
- Use "create_project" if the item describes a large initiative or goal
- Use "create_task" if the item is a specific actionable task
- Use "no_action" if the item is just a note or doesn't require action
- Keep names and descriptions concise and clear
- Infer appropriate priority based on urgency indicators in the text

Respond only with valid JSON, no additional text."""
    
    def _parse_classification_response(self, response: str) -> InboxItemClassification:
        try:
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            data = json.loads(response_clean.strip())
            return InboxItemClassification(**data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {response}")
            return InboxItemClassification(
                action=ClassificationAction.NO_ACTION,
                reasoning="Failed to parse LLM response"
            )
        except Exception as e:
            logger.error(f"Error parsing classification: {str(e)}")
            return InboxItemClassification(
                action=ClassificationAction.NO_ACTION,
                reasoning=f"Error: {str(e)}"
            )
    
    async def process_inbox_item(
        self,
        inbox_item_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        result = await self.db.get(InboxItem, inbox_item_id)
        if not result:
            raise ValueError(f"InboxItem {inbox_item_id} not found")
        
        inbox_item = result
        
        if inbox_item.status != "unprocessed":
            logger.info(f"InboxItem {inbox_item_id} already processed")
            return {"status": "already_processed", "inbox_item_id": inbox_item_id}
        
        classification = await self.classify_with_llm(inbox_item.content, user_id)
        
        project_id = None
        task_id = None
        
        if classification.action == ClassificationAction.CREATE_PROJECT:
            project = await self._create_project(
                name=classification.project_name or "Untitled Project",
                description=classification.project_description,
                owner_id=user_id
            )
            project_id = project.id
            inbox_item.project_id = project_id
        
        elif classification.action == ClassificationAction.CREATE_TASK:
            if classification.project_name:
                project = await self._create_project(
                    name=classification.project_name,
                    description=classification.project_description,
                    owner_id=user_id
                )
                project_id = project.id
                
                task = await self._create_task(
                    title=classification.task_title or "Untitled Task",
                    description=classification.task_description,
                    priority=classification.task_priority or "medium",
                    project_id=project_id,
                    assignee_id=user_id
                )
                task_id = task.id
                inbox_item.project_id = project_id
                inbox_item.task_id = task_id
            else:
                logger.warning(f"Cannot create task without project for inbox item {inbox_item_id}")
        
        inbox_item.status = "processed"
        await self.db.commit()
        await self.db.refresh(inbox_item)
        
        return {
            "status": "processed",
            "inbox_item_id": inbox_item_id,
            "classification": classification.model_dump(),
            "project_id": project_id,
            "task_id": task_id
        }
    
    async def _create_project(
        self,
        name: str,
        description: Optional[str],
        owner_id: int
    ) -> Project:
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
            status="active"
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        logger.info(f"Created project {project.id}: {name}")
        return project
    
    async def _create_task(
        self,
        title: str,
        description: Optional[str],
        priority: str,
        project_id: int,
        assignee_id: Optional[int]
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            project_id=project_id,
            assignee_id=assignee_id,
            status="pending"
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        logger.info(f"Created task {task.id}: {title}")
        return task
    
    async def _log_llm_call(
        self,
        user_id: int,
        model_name: str,
        prompt: str,
        response: Optional[str],
        tokens_used: Optional[int],
        execution_time_ms: int,
        status: str,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        log = LlmCallLog(
            user_id=user_id,
            model_name=model_name,
            prompt=prompt,
            response=response,
            tokens_used=tokens_used,
            execution_time_ms=execution_time_ms,
            status=status,
            error_message=error_message,
            extra_metadata=metadata
        )
        self.db.add(log)
        await self.db.commit()
