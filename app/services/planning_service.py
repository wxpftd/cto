import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.llm import get_llm_client
from app.models import Project, Task, PlanVersion, User, LlmCallLog
from app.core.config import settings

logger = logging.getLogger(__name__)


class PlanningService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_project_plan(
        self,
        project_id: int,
        user_id: int,
        force_regenerate: bool = False
    ) -> PlanVersion:
        result = await self.db.get(Project, project_id)
        if not result:
            raise ValueError(f"Project {project_id} not found")
        
        project = result
        
        if not force_regenerate:
            result = await self.db.execute(
                select(PlanVersion)
                .filter(PlanVersion.project_id == project_id)
                .order_by(PlanVersion.version_number.desc())
                .limit(1)
            )
            existing_plan = result.scalar_one_or_none()
            if existing_plan:
                logger.info(f"Plan already exists for project {project_id}")
                return existing_plan
        
        result = await self.db.execute(
            select(Task).filter(Task.project_id == project_id)
        )
        tasks = result.scalars().all()
        
        plan_content = await self._generate_plan_with_llm(
            project=project,
            tasks=list(tasks),
            user_id=user_id
        )
        
        result = await self.db.execute(
            select(PlanVersion)
            .filter(PlanVersion.project_id == project_id)
            .order_by(PlanVersion.version_number.desc())
            .limit(1)
        )
        latest_version = result.scalar_one_or_none()
        next_version = (latest_version.version_number + 1) if latest_version else 1
        
        plan_version = PlanVersion(
            version_number=next_version,
            content=json.dumps(plan_content),
            project_id=project_id,
            created_by=user_id
        )
        
        self.db.add(plan_version)
        await self.db.commit()
        await self.db.refresh(plan_version)
        
        logger.info(f"Generated plan version {next_version} for project {project_id}")
        return plan_version
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    async def _generate_plan_with_llm(
        self,
        project: Project,
        tasks: List[Task],
        user_id: int
    ) -> Dict[str, Any]:
        start_time = datetime.now()
        llm_client = get_llm_client()
        
        prompt = self._build_planning_prompt(project, tasks)
        
        try:
            response = await llm_client.complete(prompt, temperature=0.5, max_tokens=1500)
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            plan_content = self._parse_plan_response(response.content)
            
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
            
            return plan_content
            
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
            logger.error(f"LLM planning failed: {str(e)}")
            raise
    
    def _build_planning_prompt(self, project: Project, tasks: List[Task]) -> str:
        tasks_summary = "\n".join([
            f"- {task.title} (priority: {task.priority}, status: {task.status})"
            for task in tasks
        ])
        
        if not tasks_summary:
            tasks_summary = "No tasks yet"
        
        return f"""Create a project plan and roadmap for the following project.

Project: {project.name}
Description: {project.description or 'No description'}
Status: {project.status}

Current tasks:
{tasks_summary}

Generate a comprehensive project plan with the following structure as JSON:
{{
    "summary": "Brief summary of the project plan",
    "goals": ["goal1", "goal2", "goal3"],
    "roadmap_steps": [
        {{
            "step_number": 1,
            "title": "Step title",
            "description": "What needs to be done",
            "estimated_duration": "1 week",
            "dependencies": []
        }}
    ],
    "milestones": [
        {{
            "title": "Milestone name",
            "target_date": "relative time like 'end of month 1'",
            "deliverables": ["deliverable1", "deliverable2"]
        }}
    ],
    "risks": ["risk1", "risk2"],
    "next_steps": ["action1", "action2", "action3"]
}}

Guidelines:
- Break down the project into 3-7 major roadmap steps
- Identify key milestones and deliverables
- Consider potential risks and mitigation strategies
- Provide specific, actionable next steps
- Base recommendations on the current task list and project status

Respond only with valid JSON, no additional text."""
    
    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        try:
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            data = json.loads(response_clean.strip())
            
            required_keys = ["summary", "goals", "roadmap_steps", "milestones", "next_steps"]
            if not all(key in data for key in required_keys):
                logger.warning("Plan response missing required keys, using defaults")
                data = {
                    "summary": data.get("summary", "Project plan"),
                    "goals": data.get("goals", []),
                    "roadmap_steps": data.get("roadmap_steps", []),
                    "milestones": data.get("milestones", []),
                    "risks": data.get("risks", []),
                    "next_steps": data.get("next_steps", [])
                }
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {response}")
            return {
                "summary": "Failed to generate plan",
                "goals": [],
                "roadmap_steps": [],
                "milestones": [],
                "risks": [],
                "next_steps": []
            }
        except Exception as e:
            logger.error(f"Error parsing plan: {str(e)}")
            return {
                "summary": f"Error generating plan: {str(e)}",
                "goals": [],
                "roadmap_steps": [],
                "milestones": [],
                "risks": [],
                "next_steps": []
            }
    
    async def get_latest_plan(self, project_id: int) -> Optional[PlanVersion]:
        result = await self.db.execute(
            select(PlanVersion)
            .filter(PlanVersion.project_id == project_id)
            .order_by(PlanVersion.version_number.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
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
            metadata=metadata
        )
        self.db.add(log)
        await self.db.commit()
