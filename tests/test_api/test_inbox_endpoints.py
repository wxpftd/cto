import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, InboxItem
from app.llm.base import LLMResponse


@pytest.mark.asyncio
class TestInboxEndpoints:
    
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
    
    async def test_create_inbox_item(self, client: AsyncClient, user: User):
        """Test creating an inbox item via API"""
        response = await client.post(
            "/api/v1/inbox/",
            json={
                "content": "Build a new feature",
                "user_id": user.id,
                "tags": ["important"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Build a new feature"
        assert data["user_id"] == user.id
        assert data["status"] == "unprocessed"
        assert data["tags"] == ["important"]
        assert "id" in data
    
    async def test_create_inbox_item_without_tags(self, client: AsyncClient, user: User):
        """Test creating an inbox item without tags"""
        response = await client.post(
            "/api/v1/inbox/",
            json={
                "content": "Simple task",
                "user_id": user.id
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Simple task"
        assert data["tags"] is None
    
    async def test_create_inbox_item_invalid_data(self, client: AsyncClient, user: User):
        """Test creating an inbox item with invalid data"""
        response = await client.post(
            "/api/v1/inbox/",
            json={
                "content": "",
                "user_id": user.id
            }
        )
        
        assert response.status_code == 422
    
    @patch('app.services.inbox_service.get_llm_client')
    async def test_process_inbox_item_sync(
        self,
        mock_get_client,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User
    ):
        """Test synchronous processing of inbox item"""
        mock_client = AsyncMock()
        mock_client.complete.return_value = LLMResponse(
            content='{"action": "create_project", "project_name": "Test Project", "reasoning": "Large initiative"}',
            model="gpt-4",
            tokens_used=100
        )
        mock_get_client.return_value = mock_client
        
        inbox_item = InboxItem(
            content="Build a comprehensive project",
            user_id=user.id,
            status="unprocessed"
        )
        test_db.add(inbox_item)
        await test_db.commit()
        await test_db.refresh(inbox_item)
        
        response = await client.post(
            f"/api/v1/inbox/{inbox_item.id}/process",
            params={"user_id": user.id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["inbox_item_id"] == inbox_item.id
        assert data["project_id"] is not None
        assert "classification" in data
    
    async def test_process_inbox_item_not_found(
        self,
        client: AsyncClient,
        user: User
    ):
        """Test processing non-existent inbox item"""
        response = await client.post(
            "/api/v1/inbox/99999/process",
            params={"user_id": user.id}
        )
        
        assert response.status_code == 404
    
    async def test_get_inbox_item(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        user: User
    ):
        """Test getting an inbox item by ID"""
        inbox_item = InboxItem(
            content="Test content",
            user_id=user.id,
            status="unprocessed"
        )
        test_db.add(inbox_item)
        await test_db.commit()
        await test_db.refresh(inbox_item)
        
        response = await client.get(f"/api/v1/inbox/{inbox_item.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == inbox_item.id
        assert data["content"] == "Test content"
        assert data["user_id"] == user.id
    
    async def test_get_inbox_item_not_found(self, client: AsyncClient):
        """Test getting non-existent inbox item"""
        response = await client.get("/api/v1/inbox/99999")
        
        assert response.status_code == 404
