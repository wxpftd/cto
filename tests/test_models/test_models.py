import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.models import User, Project, Task, InboxItem, PlanVersion, Feedback, DailySummary, LlmCallLog
from app.database import Base


class TestUserModel:
    """Test User model schema and relationships"""
    
    @pytest.fixture
    def setup_database(self):
        """Set up in-memory SQLite database for testing"""
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_user_creation(self, setup_database):
        """Test User model creation"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            full_name="Test User",
            is_active=True
        )
        setup_database.add(user)
        setup_database.commit()
        setup_database.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_unique_constraints(self, setup_database):
        """Test User unique constraints on email and username"""
        # Create first user
        user1 = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user1)
        setup_database.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="test@example.com",
            username="testuser2",
            password_hash="hashed_password2"
        )
        setup_database.add(user2)
        with pytest.raises(IntegrityError):
            setup_database.commit()
        
        setup_database.rollback()
        
        # Try to create second user with same username
        user3 = User(
            email="test2@example.com",
            username="testuser",
            password_hash="hashed_password3"
        )
        setup_database.add(user3)
        with pytest.raises(IntegrityError):
            setup_database.commit()
    
    def test_user_relationships(self, setup_database):
        """Test User relationships with projects and tasks"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        
        # Create project for user
        project = Project(
            name="Test Project",
            description="Test Description",
            owner_id=user.id
        )
        setup_database.add(project)
        setup_database.commit()
        
        # Create task assigned to user
        task = Task(
            title="Test Task",
            description="Test Task Description",
            project_id=project.id,
            assignee_id=user.id
        )
        setup_database.add(task)
        setup_database.commit()
        
        # Test relationships
        assert len(user.projects) == 1
        assert user.projects[0].name == "Test Project"
        assert len(user.tasks) == 1
        assert user.tasks[0].title == "Test Task"


class TestProjectModel:
    """Test Project model schema and relationships"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def create_user_and_project(self, setup_database):
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        
        project = Project(
            name="Test Project",
            description="Test Description",
            owner_id=user.id
        )
        setup_database.add(project)
        setup_database.commit()
        setup_database.refresh(project)
        
        return user, project
    
    def test_project_creation(self, create_user_and_project):
        """Test Project model creation"""
        user, project = create_user_and_project
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.description == "Test Description"
        assert project.status == "active"
        assert project.owner_id == user.id
        assert project.owner.email == "test@example.com"
    
    def test_project_foreign_key_constraint(self, setup_database):
        """Test Project foreign key constraint to User"""
        # Try to create project with non-existent user
        project = Project(
            name="Test Project",
            owner_id=999  # Non-existent user
        )
        setup_database.add(project)
        with pytest.raises(IntegrityError):
            setup_database.commit()
    
    def test_project_status_enum(self, setup_database):
        """Test Project status enum values"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        
        for status in ['active', 'completed', 'archived']:
            project = Project(
                name=f"Project {status}",
                status=status,
                owner_id=user.id
            )
            setup_database.add(project)
            setup_database.commit()
            assert project.status == status
            setup_database.refresh(project)


class TestTaskModel:
    """Test Task model schema and relationships"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def create_complete_setup(self, setup_database):
        # Create user
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        
        # Create project
        project = Project(
            name="Test Project",
            owner_id=user.id
        )
        setup_database.add(project)
        setup_database.commit()
        
        return user, project
    
    def test_task_creation(self, create_complete_setup):
        """Test Task model creation"""
        user, project = create_complete_setup
        
        task = Task(
            title="Test Task",
            description="Test Description",
            project_id=project.id,
            assignee_id=user.id,
            priority="high",
            status="pending"
        )
        setup_database.add(task)
        setup_database.commit()
        setup_database.refresh(task)
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.project_id == project.id
        assert task.assignee_id == user.id
        assert task.priority == "high"
        assert task.status == "pending"
    
    def test_task_priority_enum(self, create_complete_setup):
        """Test Task priority enum values"""
        user, project = create_complete_setup
        
        priorities = ['low', 'medium', 'high', 'urgent']
        for i, priority in enumerate(priorities):
            task = Task(
                title=f"Task {i}",
                priority=priority,
                project_id=project.id
            )
            setup_database.add(task)
            setup_database.commit()
            assert task.priority == priority
    
    def test_task_status_enum(self, create_complete_setup):
        """Test Task status enum values"""
        user, project = create_complete_setup
        
        statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        for i, status in enumerate(statuses):
            task = Task(
                title=f"Task {i}",
                status=status,
                project_id=project.id
            )
            setup_database.add(task)
            setup_database.commit()
            assert task.status == status
    
    def test_task_relationships(self, create_complete_setup):
        """Test Task relationships"""
        user, project = create_complete_setup
        
        task = Task(
            title="Test Task",
            project_id=project.id,
            assignee_id=user.id
        )
        setup_database.add(task)
        setup_database.commit()
        setup_database.refresh(task)
        
        # Test relationship with project
        assert task.project.name == "Test Project"
        assert task.project.owner.email == "test@example.com"
        
        # Test relationship with assignee
        assert task.assignee.username == "testuser"


class TestInboxItemModel:
    """Test InboxItem model schema and relationships"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def create_complete_setup(self, setup_database):
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        
        project = Project(
            name="Test Project",
            owner_id=user.id
        )
        setup_database.add(project)
        setup_database.commit()
        
        task = Task(
            title="Test Task",
            project_id=project.id
        )
        setup_database.add(task)
        setup_database.commit()
        
        return user, project, task
    
    def test_inbox_item_creation(self, create_complete_setup):
        """Test InboxItem model creation"""
        user, project, task = create_complete_setup
        
        inbox_item = InboxItem(
            content="Test inbox content",
            user_id=user.id,
            project_id=project.id,
            task_id=task.id,
            status="unprocessed",
            tags=["tag1", "tag2"]
        )
        setup_database.add(inbox_item)
        setup_database.commit()
        setup_database.refresh(inbox_item)
        
        assert inbox_item.id is not None
        assert inbox_item.content == "Test inbox content"
        assert inbox_item.user_id == user.id
        assert inbox_item.project_id == project.id
        assert inbox_item.task_id == task.id
        assert inbox_item.status == "unprocessed"
        assert inbox_item.tags == ["tag1", "tag2"]
    
    def test_inbox_item_status_enum(self, create_complete_setup):
        """Test InboxItem status enum values"""
        user, project, task = create_complete_setup
        
        statuses = ['unprocessed', 'processed', 'archived']
        for i, status in enumerate(statuses):
            inbox_item = InboxItem(
                content=f"Content {i}",
                user_id=user.id,
                status=status
            )
            setup_database.add(inbox_item)
            setup_database.commit()
            assert inbox_item.status == status


class TestPlanVersionModel:
    """Test PlanVersion model schema and relationships"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def create_complete_setup(self, setup_database):
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        
        project = Project(
            name="Test Project",
            owner_id=user.id
        )
        setup_database.add(project)
        setup_database.commit()
        
        task = Task(
            title="Test Task",
            project_id=project.id
        )
        setup_database.add(task)
        setup_database.commit()
        
        return user, project, task
    
    def test_plan_version_project_creation(self, create_complete_setup):
        """Test PlanVersion model creation for project"""
        user, project, task = create_complete_setup
        
        plan_version = PlanVersion(
            version_number=1,
            content='{"plan": "test plan"}',
            project_id=project.id,
            created_by=user.id
        )
        setup_database.add(plan_version)
        setup_database.commit()
        setup_database.refresh(plan_version)
        
        assert plan_version.id is not None
        assert plan_version.version_number == 1
        assert plan_version.content == '{"plan": "test plan"}'
        assert plan_version.project_id == project.id
        assert plan_version.created_by == user.id
    
    def test_plan_version_task_creation(self, create_complete_setup):
        """Test PlanVersion model creation for task"""
        user, project, task = create_complete_setup
        
        plan_version = PlanVersion(
            version_number=1,
            content='{"plan": "task plan"}',
            task_id=task.id,
            created_by=user.id
        )
        setup_database.add(plan_version)
        setup_database.commit()
        setup_database.refresh(plan_version)
        
        assert plan_version.id is not None
        assert plan_version.task_id == task.id
        assert plan_version.created_by == user.id


class TestFeedbackModel:
    """Test Feedback model schema and relationships"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def create_complete_setup(self, setup_database):
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        
        project = Project(
            name="Test Project",
            owner_id=user.id
        )
        setup_database.add(project)
        setup_database.commit()
        
        task = Task(
            title="Test Task",
            project_id=project.id
        )
        setup_database.add(task)
        setup_database.commit()
        
        return user, project, task
    
    def test_feedback_creation(self, create_complete_setup):
        """Test Feedback model creation"""
        user, project, task = create_complete_setup
        
        feedback = Feedback(
            content="Test feedback",
            feedback_type="user_input",
            project_id=project.id,
            user_id=user.id,
            rating=5,
            is_resolved=False
        )
        setup_database.add(feedback)
        setup_database.commit()
        setup_database.refresh(feedback)
        
        assert feedback.id is not None
        assert feedback.content == "Test feedback"
        assert feedback.feedback_type == "user_input"
        assert feedback.project_id == project.id
        assert feedback.user_id == user.id
        assert feedback.rating == 5
        assert feedback.is_resolved is False
    
    def test_feedback_type_enum(self, create_complete_setup):
        """Test Feedback type enum values"""
        user, project, task = create_complete_setup
        
        feedback_types = ['user_input', 'system_output', 'improvement']
        for i, feedback_type in enumerate(feedback_types):
            feedback = Feedback(
                content=f"Feedback {i}",
                feedback_type=feedback_type,
                user_id=user.id
            )
            setup_database.add(feedback)
            setup_database.commit()
            assert feedback.feedback_type == feedback_type


class TestDailySummaryModel:
    """Test DailySummary model schema and relationships"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def create_complete_setup(self, setup_database):
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        
        project = Project(
            name="Test Project",
            owner_id=user.id
        )
        setup_database.add(project)
        setup_database.commit()
        
        task = Task(
            title="Test Task",
            project_id=project.id
        )
        setup_database.add(task)
        setup_database.commit()
        
        return user, task
    
    def test_daily_summary_creation(self, create_complete_setup):
        """Test DailySummary model creation"""
        user, task = create_complete_setup
        
        daily_summary = DailySummary(
            date=datetime.utcnow(),
            summary_text="Test summary",
            user_id=user.id,
            task_id=task.id,
            tasks_completed=3,
            hours_worked=240  # 4 hours in minutes
        )
        setup_database.add(daily_summary)
        setup_database.commit()
        setup_database.refresh(daily_summary)
        
        assert daily_summary.id is not None
        assert daily_summary.summary_text == "Test summary"
        assert daily_summary.user_id == user.id
        assert daily_summary.task_id == task.id
        assert daily_summary.tasks_completed == 3
        assert daily_summary.hours_worked == 240


class TestLlmCallLogModel:
    """Test LlmCallLog model schema and relationships"""
    
    @pytest.fixture
    def setup_database(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def create_user(self, setup_database):
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        setup_database.add(user)
        setup_database.commit()
        setup_database.refresh(user)
        return user
    
    def test_llm_call_log_creation(self, create_user):
        """Test LlmCallLog model creation"""
        user = create_user
        
        llm_call_log = LlmCallLog(
            user_id=user.id,
            model_name="gpt-3.5-turbo",
            prompt="Test prompt",
            response="Test response",
            tokens_used=100,
            cost_usd=50,  # 50 cents
            execution_time_ms=1000,
            status="success"
        )
        setup_database.add(llm_call_log)
        setup_database.commit()
        setup_database.refresh(llm_call_log)
        
        assert llm_call_log.id is not None
        assert llm_call_log.model_name == "gpt-3.5-turbo"
        assert llm_call_log.prompt == "Test prompt"
        assert llm_call_log.response == "Test response"
        assert llm_call_log.tokens_used == 100
        assert llm_call_log.cost_usd == 50
        assert llm_call_log.status == "success"
    
    def test_llm_call_log_status_enum(self, create_user):
        """Test LlmCallLog status enum values"""
        user = create_user
        
        statuses = ['success', 'error', 'timeout']
        for i, status in enumerate(statuses):
            llm_call_log = LlmCallLog(
                user_id=user.id,
                model_name=f"model_{i}",
                prompt=f"prompt_{i}",
                status=status
            )
            setup_database.add(llm_call_log)
            setup_database.commit()
            assert llm_call_log.status == status