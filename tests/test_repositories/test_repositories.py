import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.models import User, Project, Task, InboxItem, PlanVersion, Feedback, DailySummary, LlmCallLog
from app.database import Base
from app.repositories import (
    UserRepository, ProjectRepository, TaskRepository, InboxItemRepository,
    PlanVersionRepository, FeedbackRepository, DailySummaryRepository, LlmCallLogRepository
)


class TestUserRepository:
    """Test UserRepository CRUD operations"""
    
    @pytest.fixture
    def setup_database(self):
        """Set up in-memory SQLite database for testing"""
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def user_repository(self, setup_database):
        return UserRepository(setup_database)
    
    def test_create_user(self, user_repository):
        """Test creating a new user"""
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hashed_password',
            'full_name': 'Test User',
            'is_active': True
        }
        
        user = user_repository.create(user_data)
        
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.full_name == 'Test User'
        assert user.is_active is True
    
    def test_get_user_by_id(self, user_repository):
        """Test getting user by ID"""
        # Create user
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hashed_password'
        }
        user = user_repository.create(user_data)
        
        # Retrieve user
        retrieved_user = user_repository.get_by_id(user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
    
    def test_get_user_by_email(self, user_repository):
        """Test getting user by email"""
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hashed_password'
        }
        user_repository.create(user_data)
        
        retrieved_user = user_repository.get_by_email('test@example.com')
        
        assert retrieved_user is not None
        assert retrieved_user.email == 'test@example.com'
    
    def test_get_user_by_username(self, user_repository):
        """Test getting user by username"""
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hashed_password'
        }
        user_repository.create(user_data)
        
        retrieved_user = user_repository.get_by_username('testuser')
        
        assert retrieved_user is not None
        assert retrieved_user.username == 'testuser'
    
    def test_get_all_users(self, user_repository):
        """Test getting all users"""
        # Create multiple users
        users_data = [
            {'email': 'user1@example.com', 'username': 'user1', 'password_hash': 'hash1'},
            {'email': 'user2@example.com', 'username': 'user2', 'password_hash': 'hash2'},
            {'email': 'user3@example.com', 'username': 'user3', 'password_hash': 'hash3'},
        ]
        
        for user_data in users_data:
            user_repository.create(user_data)
        
        all_users = user_repository.get_all()
        
        assert len(all_users) == 3
    
    def test_update_user(self, user_repository):
        """Test updating a user"""
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hashed_password',
            'full_name': 'Test User'
        }
        user = user_repository.create(user_data)
        
        # Update user
        update_data = {
            'full_name': 'Updated User',
            'is_active': False
        }
        updated_user = user_repository.update(user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.full_name == 'Updated User'
        assert updated_user.is_active is False
    
    def test_delete_user(self, user_repository):
        """Test deleting a user"""
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hashed_password'
        }
        user = user_repository.create(user_data)
        
        # Delete user
        result = user_repository.delete(user.id)
        assert result is True
        
        # Try to retrieve deleted user
        deleted_user = user_repository.get_by_id(user.id)
        assert deleted_user is None
    
    def test_get_active_users(self, user_repository):
        """Test getting active users only"""
        # Create active user
        user_repository.create({
            'email': 'active@example.com',
            'username': 'activeuser',
            'password_hash': 'hash',
            'is_active': True
        })
        
        # Create inactive user
        user_repository.create({
            'email': 'inactive@example.com',
            'username': 'inactiveuser',
            'password_hash': 'hash',
            'is_active': False
        })
        
        active_users = user_repository.get_active_users()
        
        assert len(active_users) == 1
        assert active_users[0].email == 'active@example.com'


class TestProjectRepository:
    """Test ProjectRepository CRUD operations"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def project_repository(self, setup_database):
        return ProjectRepository(setup_database)
    
    @pytest.fixture
    def create_test_user(self, setup_database):
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hashed_password'
        }
        return UserRepository(setup_database).create(user_data)
    
    def test_create_project(self, project_repository, create_test_user):
        """Test creating a new project"""
        project_data = {
            'name': 'Test Project',
            'description': 'Test Description',
            'status': 'active',
            'owner_id': create_test_user.id
        }
        
        project = project_repository.create(project_data)
        
        assert project.id is not None
        assert project.name == 'Test Project'
        assert project.description == 'Test Description'
        assert project.status == 'active'
        assert project.owner_id == create_test_user.id
    
    def test_get_projects_by_owner(self, project_repository, create_test_user):
        """Test getting projects by owner"""
        # Create multiple projects for the same owner
        projects_data = [
            {'name': 'Project 1', 'owner_id': create_test_user.id},
            {'name': 'Project 2', 'owner_id': create_test_user.id},
            {'name': 'Other Project', 'owner_id': 999},  # Different owner
        ]
        
        for project_data in projects_data:
            project_repository.create(project_data)
        
        owner_projects = project_repository.get_by_owner(create_test_user.id)
        
        assert len(owner_projects) == 2
        for project in owner_projects:
            assert project.owner_id == create_test_user.id
    
    def test_get_projects_by_status(self, project_repository, create_test_user):
        """Test getting projects by status"""
        projects_data = [
            {'name': 'Active Project 1', 'status': 'active', 'owner_id': create_test_user.id},
            {'name': 'Active Project 2', 'status': 'active', 'owner_id': create_test_user.id},
            {'name': 'Completed Project', 'status': 'completed', 'owner_id': create_test_user.id},
        ]
        
        for project_data in projects_data:
            project_repository.create(project_data)
        
        active_projects = project_repository.get_by_status('active')
        
        assert len(active_projects) == 2
        for project in active_projects:
            assert project.status == 'active'
    
    def test_get_active_projects_by_owner(self, project_repository, create_test_user):
        """Test getting active projects for a specific owner"""
        projects_data = [
            {'name': 'Active Project', 'status': 'active', 'owner_id': create_test_user.id},
            {'name': 'Completed Project', 'status': 'completed', 'owner_id': create_test_user.id},
            {'name': 'Other Active', 'status': 'active', 'owner_id': 999},
        ]
        
        for project_data in projects_data:
            project_repository.create(project_data)
        
        active_projects = project_repository.get_active_projects_by_owner(create_test_user.id)
        
        assert len(active_projects) == 1
        assert active_projects[0].name == 'Active Project'


class TestTaskRepository:
    """Test TaskRepository CRUD operations"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def task_repository(self, setup_database):
        return TaskRepository(setup_database)
    
    @pytest.fixture
    def create_test_data(self, setup_database):
        # Create user
        user = UserRepository(setup_database).create({
            'email': 'user@example.com',
            'username': 'user',
            'password_hash': 'hash'
        })
        
        # Create project
        project = ProjectRepository(setup_database).create({
            'name': 'Test Project',
            'owner_id': user.id
        })
        
        return user, project
    
    def test_create_task(self, task_repository, create_test_data):
        """Test creating a new task"""
        user, project = create_test_data
        
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'status': 'pending',
            'priority': 'high',
            'project_id': project.id,
            'assignee_id': user.id
        }
        
        task = task_repository.create(task_data)
        
        assert task.id is not None
        assert task.title == 'Test Task'
        assert task.status == 'pending'
        assert task.priority == 'high'
        assert task.project_id == project.id
        assert task.assignee_id == user.id
    
    def test_get_tasks_by_project(self, task_repository, create_test_data):
        """Test getting tasks by project"""
        user, project = create_test_data
        
        tasks_data = [
            {'title': 'Task 1', 'project_id': project.id, 'assignee_id': user.id},
            {'title': 'Task 2', 'project_id': project.id, 'assignee_id': user.id},
            {'title': 'Task Other Project', 'project_id': 999, 'assignee_id': user.id},
        ]
        
        for task_data in tasks_data:
            task_repository.create(task_data)
        
        project_tasks = task_repository.get_by_project(project.id)
        
        assert len(project_tasks) == 2
        for task in project_tasks:
            assert task.project_id == project.id
    
    def test_get_tasks_by_assignee(self, task_repository, create_test_data):
        """Test getting tasks by assignee"""
        user, project = create_test_data
        
        tasks_data = [
            {'title': 'Task 1', 'project_id': project.id, 'assignee_id': user.id},
            {'title': 'Task 2', 'project_id': project.id, 'assignee_id': user.id},
            {'title': 'Task Other User', 'project_id': project.id, 'assignee_id': 999},
        ]
        
        for task_data in tasks_data:
            task_repository.create(task_data)
        
        assignee_tasks = task_repository.get_by_assignee(user.id)
        
        assert len(assignee_tasks) == 2
        for task in assignee_tasks:
            assert task.assignee_id == user.id
    
    def test_get_tasks_by_status(self, task_repository, create_test_data):
        """Test getting tasks by status"""
        user, project = create_test_data
        
        tasks_data = [
            {'title': 'Pending Task 1', 'status': 'pending', 'project_id': project.id},
            {'title': 'Pending Task 2', 'status': 'pending', 'project_id': project.id},
            {'title': 'In Progress Task', 'status': 'in_progress', 'project_id': project.id},
        ]
        
        for task_data in tasks_data:
            task_repository.create(task_data)
        
        pending_tasks = task_repository.get_by_status('pending')
        
        assert len(pending_tasks) == 2
        for task in pending_tasks:
            assert task.status == 'pending'


class TestInboxItemRepository:
    """Test InboxItemRepository CRUD operations"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def inbox_repository(self, setup_database):
        return InboxItemRepository(setup_database)
    
    @pytest.fixture
    def create_test_data(self, setup_database):
        user = UserRepository(setup_database).create({
            'email': 'user@example.com',
            'username': 'user',
            'password_hash': 'hash'
        })
        project = ProjectRepository(setup_database).create({
            'name': 'Test Project',
            'owner_id': user.id
        })
        return user, project
    
    def test_create_inbox_item(self, inbox_repository, create_test_data):
        """Test creating a new inbox item"""
        user, project = create_test_data
        
        inbox_data = {
            'content': 'Test inbox content',
            'user_id': user.id,
            'project_id': project.id,
            'status': 'unprocessed',
            'tags': ['tag1', 'tag2']
        }
        
        inbox_item = inbox_repository.create(inbox_data)
        
        assert inbox_item.id is not None
        assert inbox_item.content == 'Test inbox content'
        assert inbox_item.user_id == user.id
        assert inbox_item.status == 'unprocessed'
        assert inbox_item.tags == ['tag1', 'tag2']
    
    def test_get_inbox_items_by_user(self, inbox_repository, create_test_data):
        """Test getting inbox items by user"""
        user, project = create_test_data
        
        items_data = [
            {'content': 'Item 1', 'user_id': user.id},
            {'content': 'Item 2', 'user_id': user.id},
            {'content': 'Item Other User', 'user_id': 999},
        ]
        
        for item_data in items_data:
            inbox_repository.create(item_data)
        
        user_items = inbox_repository.get_by_user(user.id)
        
        assert len(user_items) == 2
        for item in user_items:
            assert item.user_id == user.id
    
    def test_get_unprocessed_items_by_user(self, inbox_repository, create_test_data):
        """Test getting unprocessed inbox items for a user"""
        user, project = create_test_data
        
        items_data = [
            {'content': 'Unprocessed 1', 'user_id': user.id, 'status': 'unprocessed'},
            {'content': 'Processed 1', 'user_id': user.id, 'status': 'processed'},
            {'content': 'Unprocessed 2', 'user_id': user.id, 'status': 'unprocessed'},
        ]
        
        for item_data in items_data:
            inbox_repository.create(item_data)
        
        unprocessed_items = inbox_repository.get_unprocessed_by_user(user.id)
        
        assert len(unprocessed_items) == 2
        for item in unprocessed_items:
            assert item.status == 'unprocessed'


class TestRepositoryCRUD:
    """Test generic CRUD operations for all repositories"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.mark.parametrize("repository_class,create_data,expected_field", [
        (UserRepository, {'email': 'test@example.com', 'username': 'testuser', 'password_hash': 'hash'}, 'email'),
        (ProjectRepository, {'name': 'Test Project', 'owner_id': 1}, 'name'),
        (TaskRepository, {'title': 'Test Task', 'project_id': 1}, 'title'),
        (InboxItemRepository, {'content': 'Test content', 'user_id': 1}, 'content'),
        (PlanVersionRepository, {'version_number': 1, 'content': 'test', 'created_by': 1}, 'version_number'),
        (FeedbackRepository, {'content': 'test feedback', 'feedback_type': 'user_input', 'user_id': 1}, 'content'),
        (DailySummaryRepository, {'date': datetime.utcnow(), 'summary_text': 'test', 'user_id': 1}, 'summary_text'),
        (LlmCallLogRepository, {'user_id': 1, 'model_name': 'test', 'prompt': 'test'}, 'model_name'),
    ])
    def test_repository_create(self, setup_database, repository_class, create_data, expected_field):
        """Test generic create operation for all repositories"""
        repository = repository_class(setup_database)
        
        # For repositories that need related entities, create them first
        if repository_class == ProjectRepository:
            user_data = {'email': 'test@example.com', 'username': 'testuser', 'password_hash': 'hash'}
            UserRepository(setup_database).create(user_data)
        elif repository_class == TaskRepository:
            user_data = {'email': 'test@example.com', 'username': 'testuser', 'password_hash': 'hash'}
            user = UserRepository(setup_database).create(user_data)
            project_data = {'name': 'Test Project', 'owner_id': user.id}
            ProjectRepository(setup_database).create(project_data)
        elif repository_class in [PlanVersionRepository, FeedbackRepository]:
            user_data = {'email': 'test@example.com', 'username': 'testuser', 'password_hash': 'hash'}
            user = UserRepository(setup_database).create(user_data)
            if repository_class == FeedbackRepository:
                create_data['user_id'] = user.id
            else:
                create_data['created_by'] = user.id
        elif repository_class == DailySummaryRepository:
            user_data = {'email': 'test@example.com', 'username': 'testuser', 'password_hash': 'hash'}
            UserRepository(setup_database).create(user_data)
        elif repository_class == LlmCallLogRepository:
            user_data = {'email': 'test@example.com', 'username': 'testuser', 'password_hash': 'hash'}
            UserRepository(setup_database).create(user_data)
        
        record = repository.create(create_data)
        
        assert record.id is not None
        assert getattr(record, expected_field) == create_data[expected_field]