import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.inbox_service import InboxService
from app.schemas.inbox import ClassificationAction, InboxItemClassification
from app.models import User, InboxItem, Project, Task, LlmCallLog
from app.llm.base import LLMResponse


@pytest.mark.asyncio
class TestInboxService:
    
    @pytest_asyncio.fixture
    async def user(self, test_db: AsyncSession):
        """Create a test user"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            full_name="Test User"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user
    
    async def test_create_inbox_item(self, test_db: AsyncSession, user: User):
        """Test creating an inbox item"""
        service = InboxService(test_db)
        
        inbox_item = await service.create_inbox_item(
            content="Build a new feature",
            user_id=user.id,
            tags=["important", "feature"]
        )
        
        assert inbox_item.id is not None
        assert inbox_item.content == "Build a new feature"
        assert inbox_item.user_id == user.id
        assert inbox_item.status == "unprocessed"
        assert inbox_item.tags == ["important", "feature"]
    
    async def test_build_classification_prompt(self, test_db: AsyncSession):
        """Test building classification prompt"""
        service = InboxService(test_db)
        
        prompt = service._build_classification_prompt("Build a website")
        
        assert "Build a website" in prompt
        assert "create_project" in prompt
        assert "create_task" in prompt
        assert "JSON" in prompt
    
    async def test_parse_classification_response_valid_json(self, test_db: AsyncSession):
        """Test parsing valid JSON classification response"""
        service = InboxService(test_db)
        
        response = """
        {
            "action": "create_project",
            "project_name": "Website Project",
            "project_description": "Build a new website",
            "reasoning": "This is a large initiative"
        }
        """
        
        classification = service._parse_classification_response(response)
        
        assert classification.action == ClassificationAction.CREATE_PROJECT
        assert classification.project_name == "Website Project"
        assert classification.project_description == "Build a new website"
    
    async def test_parse_classification_response_with_code_block(self, test_db: AsyncSession):
        """Test parsing JSON wrapped in markdown code block"""
        service = InboxService(test_db)
        
        response = """```json
        {
            "action": "create_task",
            "task_title": "Fix bug",
            "task_priority": "high",
            "reasoning": "This is urgent"
        }
        ```"""
        
        classification = service._parse_classification_response(response)
        
        assert classification.action == ClassificationAction.CREATE_TASK
        assert classification.task_title == "Fix bug"
        assert classification.task_priority == "high"
    
    async def test_parse_classification_response_invalid_json(self, test_db: AsyncSession):
        """Test parsing invalid JSON returns no_action"""
        service = InboxService(test_db)
        
        response = "This is not valid JSON"
        
        classification = service._parse_classification_response(response)
        
        assert classification.action == ClassificationAction.NO_ACTION
        assert "Failed to parse" in classification.reasoning
    
    @patch('app.services.inbox_service.get_llm_client')
    async def test_classify_with_llm_success(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User
    ):
        """Test successful LLM classification"""
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content='{"action": "create_project", "project_name": "Test Project", "reasoning": "Test"}',
            model="gpt-4",
            tokens_used=100,
            metadata={"prompt_tokens": 50, "completion_tokens": 50}
        )
        mock_get_client.return_value = mock_client
        
        service = InboxService(test_db)
        
        classification = await service.classify_with_llm(
            content="Build a new app",
            user_id=user.id
        )
        
        assert classification.action == ClassificationAction.CREATE_PROJECT
        assert classification.project_name == "Test Project"
        
        mock_client.complete.assert_called_once()
        
        from sqlalchemy import select
        result = await test_db.execute(
            select(LlmCallLog).filter(LlmCallLog.user_id == user.id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].status == "success"
        assert logs[0].tokens_used == 100
    
    @patch('app.services.inbox_service.get_llm_client')
    async def test_classify_with_llm_error(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User
    ):
        """Test LLM classification with error"""
        mock_client = AsyncMock()
        mock_client.complete.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        
        service = InboxService(test_db)
        
        with pytest.raises(Exception, match="API Error"):
            await service.classify_with_llm(
                content="Build a new app",
                user_id=user.id
            )
        
        from sqlalchemy import select
        result = await test_db.execute(
            select(LlmCallLog).filter(LlmCallLog.user_id == user.id)
        )
        logs = result.scalars().all()
        # Should have 3 log entries due to retry logic (3 attempts)
        assert len(logs) == 3
        assert all(log.status == "error" for log in logs)
        assert all("API Error" in log.error_message for log in logs)
    
    @patch('app.services.inbox_service.get_llm_client')
    async def test_process_inbox_item_create_project(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User
    ):
        """Test processing inbox item that creates a project"""
        mock_client = AsyncMock()
        mock_client.complete.side_effect = [
            LLMResponse(
                content='{"action": "create_project", "project_name": "My Project", "project_description": "A test project", "reasoning": "Large initiative"}',
                model="gpt-4",
                tokens_used=100
            ),
            LLMResponse(
                content='{"summary": "Plan", "goals": [], "roadmap_steps": [], "milestones": [], "risks": [], "next_steps": []}',
                model="gpt-4",
                tokens_used=100
            )
        ]
        mock_get_client.return_value = mock_client
        
        service = InboxService(test_db)
        
        inbox_item = await service.create_inbox_item(
            content="Build a comprehensive project management system",
            user_id=user.id
        )
        
        result = await service.process_inbox_item(inbox_item.id, user.id, trigger_planning=True)
        
        assert result["status"] == "processed"
        assert result["project_id"] is not None
        assert result["task_id"] is None
        assert result.get("plan_generated") is True
        
        await test_db.refresh(inbox_item)
        assert inbox_item.status == "processed"
        assert inbox_item.project_id is not None
        
        project = await test_db.get(Project, inbox_item.project_id)
        assert project is not None
        assert project.name == "My Project"
        assert project.description == "A test project"
        assert project.owner_id == user.id
    
    @patch('app.services.inbox_service.get_llm_client')
    async def test_process_inbox_item_create_task(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User
    ):
        """Test processing inbox item that creates a project and task"""
        mock_client = AsyncMock()
        mock_client.complete.side_effect = [
            LLMResponse(
                content='{"action": "create_task", "project_name": "Website", "task_title": "Fix homepage", "task_description": "Fix the bug on homepage", "task_priority": "high", "reasoning": "Specific task"}',
                model="gpt-4",
                tokens_used=100
            ),
            LLMResponse(
                content='{"summary": "Plan", "goals": [], "roadmap_steps": [], "milestones": [], "risks": [], "next_steps": []}',
                model="gpt-4",
                tokens_used=100
            )
        ]
        mock_get_client.return_value = mock_client
        
        service = InboxService(test_db)
        
        inbox_item = await service.create_inbox_item(
            content="Fix the homepage loading issue",
            user_id=user.id
        )
        
        result = await service.process_inbox_item(inbox_item.id, user.id, trigger_planning=True)
        
        assert result["status"] == "processed"
        assert result["project_id"] is not None
        assert result["task_id"] is not None
        assert result.get("plan_generated") is True
        
        await test_db.refresh(inbox_item)
        assert inbox_item.status == "processed"
        assert inbox_item.project_id is not None
        assert inbox_item.task_id is not None
        
        task = await test_db.get(Task, inbox_item.task_id)
        assert task is not None
        assert task.title == "Fix homepage"
        assert task.description == "Fix the bug on homepage"
        assert task.priority == "high"
        assert task.assignee_id == user.id
    
    @patch('app.services.inbox_service.get_llm_client')
    async def test_process_inbox_item_no_action(
        self,
        mock_get_client,
        test_db: AsyncSession,
        user: User
    ):
        """Test processing inbox item with no action"""
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content='{"action": "no_action", "reasoning": "Just a note"}',
            model="gpt-4",
            tokens_used=50
        )
        mock_get_client.return_value = mock_client
        
        service = InboxService(test_db)
        
        inbox_item = await service.create_inbox_item(
            content="Remember to buy milk",
            user_id=user.id
        )
        
        result = await service.process_inbox_item(inbox_item.id, user.id)
        
        assert result["status"] == "processed"
        assert result["project_id"] is None
        assert result["task_id"] is None
        
        await test_db.refresh(inbox_item)
        assert inbox_item.status == "processed"
    
    async def test_process_inbox_item_already_processed(
        self,
        test_db: AsyncSession,
        user: User
    ):
        """Test processing an already processed inbox item"""
        service = InboxService(test_db)
        
        inbox_item = await service.create_inbox_item(
            content="Test item",
            user_id=user.id
        )
        
        inbox_item.status = "processed"
        await test_db.commit()
        
        result = await service.process_inbox_item(inbox_item.id, user.id)
        
        assert result["status"] == "already_processed"
    
    async def test_process_inbox_item_not_found(
        self,
        test_db: AsyncSession,
        user: User
    ):
        """Test processing non-existent inbox item"""
        service = InboxService(test_db)
        
        with pytest.raises(ValueError, match="not found"):
            await service.process_inbox_item(99999, user.id)
