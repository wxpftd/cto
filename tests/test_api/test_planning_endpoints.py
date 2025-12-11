import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.models import User, Project, Task, PlanVersion, DailySummary
from app.llm.base import LLMResponse
from datetime import datetime, timedelta


@pytest.mark.asyncio
class TestPlanningEndpoints:
    
    @pytest_asyncio.fixture
    async def user(self, test_db: AsyncSession):
        user = User(
            email="api@example.com",
            username="apiuser",
            password_hash="hashed_password",
            full_name="API User"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user
    
    @pytest_asyncio.fixture
    async def project(self, test_db: AsyncSession, user: User):
        project = Project(
            name="API Test Project",
            description="Project for API testing",
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
                title="Task 1",
                priority="urgent",
                status="pending",
                project_id=project.id,
                assignee_id=user.id,
                due_date=datetime.now()
            ),
            Task(
                title="Task 2",
                priority="high",
                status="in_progress",
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
    
    @patch('app.services.planning_service.get_llm_client')
    async def test_generate_plan(
        self,
        mock_get_client,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        project: Project,
        tasks: list
    ):
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content=json.dumps({
                "summary": "Test plan",
                "goals": ["Goal 1"],
                "roadmap_steps": [
                    {
                        "step_number": 1,
                        "title": "Step 1",
                        "description": "First step",
                        "estimated_duration": "1 week",
                        "dependencies": []
                    }
                ],
                "milestones": [
                    {
                        "title": "Milestone 1",
                        "target_date": "end of month",
                        "deliverables": ["Deliverable 1"]
                    }
                ],
                "risks": ["Risk 1"],
                "next_steps": ["Action 1"]
            }),
            model="gpt-4",
            tokens_used=300
        )
        mock_get_client.return_value = mock_client
        
        response = await client.post(
            "/api/v1/planning/generate",
            json={
                "project_id": project.id,
                "user_id": user.id,
                "force_regenerate": False
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["version_number"] == 1
        assert data["project_id"] == project.id
        assert data["created_by"] == user.id
        assert "content" in data
    
    @patch('app.services.planning_service.get_llm_client')
    async def test_generate_plan_force_regenerate(
        self,
        mock_get_client,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        project: Project,
        tasks: list
    ):
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content=json.dumps({
                "summary": "Test plan",
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
        
        response1 = await client.post(
            "/api/v1/planning/generate",
            json={
                "project_id": project.id,
                "user_id": user.id,
                "force_regenerate": False
            }
        )
        
        response2 = await client.post(
            "/api/v1/planning/generate",
            json={
                "project_id": project.id,
                "user_id": user.id,
                "force_regenerate": True
            }
        )
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["version_number"] == 1
        assert data2["version_number"] == 2
    
    async def test_generate_plan_project_not_found(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User
    ):
        response = await client.post(
            "/api/v1/planning/generate",
            json={
                "project_id": 99999,
                "user_id": user.id,
                "force_regenerate": False
            }
        )
        
        assert response.status_code == 404
    
    async def test_get_latest_plan(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        project: Project
    ):
        plan = PlanVersion(
            version_number=1,
            content=json.dumps({"summary": "Test plan"}),
            project_id=project.id,
            created_by=user.id
        )
        test_db.add(plan)
        await test_db.commit()
        await test_db.refresh(plan)
        
        response = await client.get(
            f"/api/v1/planning/projects/{project.id}/latest"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["version_number"] == 1
        assert data["project_id"] == project.id
    
    async def test_get_latest_plan_not_found(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        project: Project
    ):
        response = await client.get(
            f"/api/v1/planning/projects/{project.id}/latest"
        )
        
        assert response.status_code == 404
    
    async def test_get_plan_content(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        project: Project
    ):
        content = {
            "summary": "Test plan content",
            "goals": ["Goal 1", "Goal 2"],
            "roadmap_steps": [],
            "milestones": [],
            "risks": [],
            "next_steps": ["Action 1"]
        }
        
        plan = PlanVersion(
            version_number=1,
            content=json.dumps(content),
            project_id=project.id,
            created_by=user.id
        )
        test_db.add(plan)
        await test_db.commit()
        
        response = await client.get(
            f"/api/v1/planning/projects/{project.id}/content"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Test plan content"
        assert len(data["goals"]) == 2
        assert len(data["next_steps"]) == 1
    
    async def test_generate_daily_plan(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        tasks: list
    ):
        response = await client.post(
            "/api/v1/planning/daily/generate",
            json={
                "user_id": user.id,
                "target_date": None
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
        
        if len(data) > 0:
            assert data[0]["user_id"] == user.id
            assert "summary_text" in data[0]
            assert "task_id" in data[0]
    
    async def test_get_today_plan(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        tasks: list
    ):
        response = await client.get(
            f"/api/v1/planning/daily/today/{user.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            assert data[0]["user_id"] == user.id
    
    async def test_mark_task_complete(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        tasks: list
    ):
        task_to_complete = tasks[0]
        
        response = await client.post(
            "/api/v1/planning/daily/generate",
            json={"user_id": user.id}
        )
        
        response = await client.post(
            "/api/v1/planning/tasks/complete",
            json={
                "task_id": task_to_complete.id,
                "user_id": user.id,
                "hours_worked": 120
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_to_complete.id
        assert data["status"] == "completed"
        assert "completed_at" in data
    
    async def test_mark_task_complete_not_found(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User
    ):
        response = await client.post(
            "/api/v1/planning/tasks/complete",
            json={
                "task_id": 99999,
                "user_id": user.id,
                "hours_worked": 60
            }
        )
        
        assert response.status_code == 404
    
    async def test_get_daily_summary(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        tasks: list
    ):
        today = datetime.now()
        
        summary = DailySummary(
            date=today,
            summary_text="Test summary",
            user_id=user.id,
            task_id=tasks[0].id,
            tasks_completed=1,
            hours_worked=60
        )
        test_db.add(summary)
        await test_db.commit()
        
        response = await client.get(
            f"/api/v1/planning/daily/summary/{user.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] >= 1
        assert data["completed_tasks"] >= 1
        assert "completion_rate" in data
        assert "summaries" in data
    
    async def test_get_daily_summary_with_date(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User,
        tasks: list
    ):
        yesterday = datetime.now() - timedelta(days=1)
        
        summary = DailySummary(
            date=yesterday,
            summary_text="Yesterday's summary",
            user_id=user.id,
            task_id=tasks[0].id,
            tasks_completed=0,
            hours_worked=0
        )
        test_db.add(summary)
        await test_db.commit()
        
        response = await client.get(
            f"/api/v1/planning/daily/summary/{user.id}",
            params={"date": yesterday.isoformat()}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] >= 1
