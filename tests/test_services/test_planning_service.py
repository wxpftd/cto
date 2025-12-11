import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.services.planning_service import PlanningService
from app.models import User, Project, Task, PlanVersion, LlmCallLog
from app.llm.base import LLMResponse


@pytest.mark.asyncio
class TestPlanningService:
    
    @pytest_asyncio.fixture
    async def user(self, test_db: AsyncSession):
        user = User(
            email="planner@example.com",
            username="planner",
            password_hash="hashed_password",
            full_name="Planning User"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user
    
    @pytest_asyncio.fixture
    async def project(self, test_db: AsyncSession, user: User):
        project = Project(
            name="Test Project",
            description="A test project for planning",
            owner_id=user.id,
            status="active"
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)
        return project
    
    @pytest_asyncio.fixture
    async def tasks(self, test_db: AsyncSession, project: Project, user: User):
        tasks = [
            Task(
                title="Setup infrastructure",
                description="Setup cloud infrastructure",
                priority="high",
                status="pending",
                project_id=project.id,
                assignee_id=user.id
            ),
            Task(
                title="Implement API",
                description="Build REST API endpoints",
                priority="medium",
                status="pending",
                project_id=project.id,
                assignee_id=user.id
            ),
            Task(
                title="Write tests",
                description="Add unit tests",
                priority="medium",
                status="pending",
                project_id=project.id,
                assignee_id=user.id
            )
        ]
        for task in tasks:
            test_db.add(task)
        await test_db.commit()
        for task in tasks:
            await test_db.refresh(task)
        return tasks
    
    async def test_build_planning_prompt(self, test_db: AsyncSession, project: Project, tasks: list):
        service = PlanningService(test_db)
        
        prompt = service._build_planning_prompt(project, tasks)
        
        assert "Test Project" in prompt
        assert "A test project for planning" in prompt
        assert "Setup infrastructure" in prompt
        assert "Implement API" in prompt
        assert "roadmap_steps" in prompt
        assert "milestones" in prompt
    
    async def test_parse_plan_response_valid_json(self, test_db: AsyncSession):
        service = PlanningService(test_db)
        
        response = """
        {
            "summary": "Comprehensive project plan for building a web application",
            "goals": ["Launch MVP", "Onboard users", "Scale system"],
            "roadmap_steps": [
                {
                    "step_number": 1,
                    "title": "Foundation",
                    "description": "Setup infrastructure and core services",
                    "estimated_duration": "2 weeks",
                    "dependencies": []
                },
                {
                    "step_number": 2,
                    "title": "Development",
                    "description": "Build features",
                    "estimated_duration": "4 weeks",
                    "dependencies": [1]
                }
            ],
            "milestones": [
                {
                    "title": "MVP Launch",
                    "target_date": "end of month 2",
                    "deliverables": ["Working app", "Basic features"]
                }
            ],
            "risks": ["Technical debt", "Scope creep"],
            "next_steps": ["Start infrastructure setup", "Define API contracts"]
        }
        """
        
        plan = service._parse_plan_response(response)
        
        assert plan["summary"] == "Comprehensive project plan for building a web application"
        assert len(plan["goals"]) == 3
        assert len(plan["roadmap_steps"]) == 2
        assert plan["roadmap_steps"][0]["step_number"] == 1
        assert plan["roadmap_steps"][0]["title"] == "Foundation"
        assert len(plan["milestones"]) == 1
        assert len(plan["risks"]) == 2
        assert len(plan["next_steps"]) == 2
    
    async def test_parse_plan_response_with_code_block(self, test_db: AsyncSession):
        service = PlanningService(test_db)
        
        response = """```json
        {
            "summary": "Test plan",
            "goals": ["Goal 1"],
            "roadmap_steps": [],
            "milestones": [],
            "risks": [],
            "next_steps": ["Step 1"]
        }
        ```"""
        
        plan = service._parse_plan_response(response)
        
        assert plan["summary"] == "Test plan"
        assert len(plan["goals"]) == 1
    
    async def test_parse_plan_response_invalid_json(self, test_db: AsyncSession):
        service = PlanningService(test_db)
        
        response = "This is not valid JSON"
        
        plan = service._parse_plan_response(response)
        
        assert "Failed to generate plan" in plan["summary"]
        assert plan["goals"] == []
        assert plan["roadmap_steps"] == []
    
    async def test_parse_plan_response_missing_keys(self, test_db: AsyncSession):
        service = PlanningService(test_db)
        
        response = '{"summary": "Partial plan", "goals": ["Goal 1"]}'
        
        plan = service._parse_plan_response(response)
        
        assert plan["summary"] == "Partial plan"
        assert plan["goals"] == ["Goal 1"]
        assert plan["roadmap_steps"] == []
        assert plan["milestones"] == []
        assert plan["next_steps"] == []
    
    @patch('app.services.planning_service.get_llm_client')
    async def test_generate_project_plan_success(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User,
        project: Project,
        tasks: list
    ):
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content=json.dumps({
                "summary": "Test plan for the project",
                "goals": ["Goal 1", "Goal 2"],
                "roadmap_steps": [
                    {
                        "step_number": 1,
                        "title": "Setup",
                        "description": "Initial setup",
                        "estimated_duration": "1 week",
                        "dependencies": []
                    }
                ],
                "milestones": [
                    {
                        "title": "First milestone",
                        "target_date": "end of month 1",
                        "deliverables": ["Deliverable 1"]
                    }
                ],
                "risks": ["Risk 1"],
                "next_steps": ["Action 1", "Action 2"]
            }),
            model="gpt-4",
            tokens_used=500,
            metadata={"prompt_tokens": 300, "completion_tokens": 200}
        )
        mock_get_client.return_value = mock_client
        
        service = PlanningService(test_db)
        
        plan_version = await service.generate_project_plan(
            project_id=project.id,
            user_id=user.id
        )
        
        assert plan_version.id is not None
        assert plan_version.version_number == 1
        assert plan_version.project_id == project.id
        assert plan_version.created_by == user.id
        
        content = json.loads(plan_version.content)
        assert content["summary"] == "Test plan for the project"
        assert len(content["goals"]) == 2
        assert len(content["roadmap_steps"]) == 1
        assert content["roadmap_steps"][0]["title"] == "Setup"
        
        mock_client.complete.assert_called_once()
        
        from sqlalchemy import select
        result = await test_db.execute(
            select(LlmCallLog).filter(LlmCallLog.user_id == user.id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].status == "success"
        assert logs[0].tokens_used == 500
    
    @patch('app.services.planning_service.get_llm_client')
    async def test_generate_project_plan_increments_version(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User,
        project: Project,
        tasks: list
    ):
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content=json.dumps({
                "summary": "Plan",
                "goals": [],
                "roadmap_steps": [],
                "milestones": [],
                "risks": [],
                "next_steps": []
            }),
            model="gpt-4",
            tokens_used=100
        )
        mock_get_client.return_value = mock_client
        
        service = PlanningService(test_db)
        
        plan_v1 = await service.generate_project_plan(
            project_id=project.id,
            user_id=user.id,
            force_regenerate=False
        )
        assert plan_v1.version_number == 1
        
        plan_v2 = await service.generate_project_plan(
            project_id=project.id,
            user_id=user.id,
            force_regenerate=True
        )
        assert plan_v2.version_number == 2
    
    @patch('app.services.planning_service.get_llm_client')
    async def test_generate_project_plan_without_force_returns_existing(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User,
        project: Project,
        tasks: list
    ):
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content=json.dumps({
                "summary": "Plan",
                "goals": [],
                "roadmap_steps": [],
                "milestones": [],
                "risks": [],
                "next_steps": []
            }),
            model="gpt-4",
            tokens_used=100
        )
        mock_get_client.return_value = mock_client
        
        service = PlanningService(test_db)
        
        plan_v1 = await service.generate_project_plan(
            project_id=project.id,
            user_id=user.id
        )
        
        plan_v2 = await service.generate_project_plan(
            project_id=project.id,
            user_id=user.id,
            force_regenerate=False
        )
        
        assert plan_v1.id == plan_v2.id
        assert plan_v2.version_number == 1
        assert mock_client.complete.call_count == 1
    
    async def test_generate_project_plan_project_not_found(
        self,
        test_db: AsyncSession,
        user: User
    ):
        service = PlanningService(test_db)
        
        with pytest.raises(ValueError, match="not found"):
            await service.generate_project_plan(
                project_id=99999,
                user_id=user.id
            )
    
    @patch('app.services.planning_service.get_llm_client')
    async def test_generate_project_plan_with_empty_tasks(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User,
        project: Project
    ):
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content=json.dumps({
                "summary": "Plan for empty project",
                "goals": ["Create initial tasks"],
                "roadmap_steps": [],
                "milestones": [],
                "risks": [],
                "next_steps": ["Define tasks"]
            }),
            model="gpt-4",
            tokens_used=100
        )
        mock_get_client.return_value = mock_client
        
        service = PlanningService(test_db)
        
        plan_version = await service.generate_project_plan(
            project_id=project.id,
            user_id=user.id
        )
        
        assert plan_version.id is not None
        
        prompt_arg = mock_client.complete.call_args[0][0]
        assert "No tasks yet" in prompt_arg
    
    async def test_get_latest_plan(
        self,
        test_db: AsyncSession,
        user: User,
        project: Project
    ):
        plan1 = PlanVersion(
            version_number=1,
            content=json.dumps({"summary": "Plan v1"}),
            project_id=project.id,
            created_by=user.id
        )
        test_db.add(plan1)
        
        plan2 = PlanVersion(
            version_number=2,
            content=json.dumps({"summary": "Plan v2"}),
            project_id=project.id,
            created_by=user.id
        )
        test_db.add(plan2)
        
        await test_db.commit()
        
        service = PlanningService(test_db)
        latest = await service.get_latest_plan(project.id)
        
        assert latest is not None
        assert latest.version_number == 2
    
    async def test_get_latest_plan_no_plan_exists(
        self,
        test_db: AsyncSession,
        project: Project
    ):
        service = PlanningService(test_db)
        latest = await service.get_latest_plan(project.id)
        
        assert latest is None
    
    @patch('app.services.planning_service.get_llm_client')
    async def test_generate_plan_llm_error_logging(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User,
        project: Project,
        tasks: list
    ):
        mock_client = AsyncMock()
        mock_client.complete.side_effect = Exception("LLM API Error")
        mock_get_client.return_value = mock_client
        
        service = PlanningService(test_db)
        
        with pytest.raises(Exception, match="LLM API Error"):
            await service.generate_project_plan(
                project_id=project.id,
                user_id=user.id
            )
        
        from sqlalchemy import select
        result = await test_db.execute(
            select(LlmCallLog).filter(LlmCallLog.user_id == user.id)
        )
        logs = result.scalars().all()
        assert len(logs) == 3
        assert all(log.status == "error" for log in logs)
        assert all("LLM API Error" in log.error_message for log in logs)
