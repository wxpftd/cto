import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.services.daily_planning_service import DailyPlanningService
from app.models import User, Project, Task, DailySummary


@pytest.mark.asyncio
class TestDailyPlanningService:
    
    @pytest_asyncio.fixture
    async def user(self, test_db: AsyncSession):
        user = User(
            email="daily@example.com",
            username="dailyuser",
            password_hash="hashed_password",
            full_name="Daily User"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user
    
    @pytest_asyncio.fixture
    async def project(self, test_db: AsyncSession, user: User):
        project = Project(
            name="Daily Project",
            description="Project for daily planning",
            owner_id=user.id,
            status="active"
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)
        return project
    
    @pytest_asyncio.fixture
    async def tasks_with_priorities(self, test_db: AsyncSession, project: Project, user: User):
        today = datetime.now()
        
        tasks = [
            Task(
                title="Urgent bug fix",
                description="Fix critical production bug",
                priority="urgent",
                status="pending",
                project_id=project.id,
                assignee_id=user.id,
                due_date=today
            ),
            Task(
                title="High priority feature",
                description="Implement important feature",
                priority="high",
                status="in_progress",
                project_id=project.id,
                assignee_id=user.id,
                due_date=today + timedelta(days=2)
            ),
            Task(
                title="Medium priority task",
                description="Regular task",
                priority="medium",
                status="pending",
                project_id=project.id,
                assignee_id=user.id,
                due_date=today + timedelta(days=7)
            ),
            Task(
                title="Low priority task",
                description="Can wait",
                priority="low",
                status="pending",
                project_id=project.id,
                assignee_id=user.id,
                due_date=today + timedelta(days=30)
            ),
            Task(
                title="Already completed",
                description="Done task",
                priority="high",
                status="completed",
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
    
    async def test_calculate_task_score_urgent_priority(
        self,
        test_db: AsyncSession,
        project: Project,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        task = Task(
            title="Urgent task",
            priority="urgent",
            status="pending",
            project_id=project.id,
            assignee_id=user.id
        )
        
        score = service._calculate_task_score(task, datetime.now())
        
        assert score == 40
    
    async def test_calculate_task_score_in_progress_bonus(
        self,
        test_db: AsyncSession,
        project: Project,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        task = Task(
            title="In progress task",
            priority="medium",
            status="in_progress",
            project_id=project.id,
            assignee_id=user.id
        )
        
        score = service._calculate_task_score(task, datetime.now())
        
        assert score == 35
    
    async def test_calculate_task_score_overdue(
        self,
        test_db: AsyncSession,
        project: Project,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        yesterday = datetime.now() - timedelta(days=1)
        
        task = Task(
            title="Overdue task",
            priority="medium",
            status="pending",
            project_id=project.id,
            assignee_id=user.id,
            due_date=yesterday
        )
        
        score = service._calculate_task_score(task, datetime.now())
        
        assert score >= 70
    
    async def test_calculate_task_score_due_today(
        self,
        test_db: AsyncSession,
        project: Project,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        today = datetime.now()
        
        task = Task(
            title="Due today",
            priority="medium",
            status="pending",
            project_id=project.id,
            assignee_id=user.id,
            due_date=today
        )
        
        score = service._calculate_task_score(task, datetime.now())
        
        assert score >= 60
    
    async def test_generate_daily_plan_selects_top_three(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        summaries = await service.generate_daily_plan(user_id=user.id)
        
        assert len(summaries) <= 3
        assert all(isinstance(s, DailySummary) for s in summaries)
        assert all(s.user_id == user.id for s in summaries)
        
        task_ids = [s.task_id for s in summaries]
        assert tasks_with_priorities[0].id in task_ids
        assert tasks_with_priorities[1].id in task_ids
    
    async def test_generate_daily_plan_excludes_completed_tasks(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        summaries = await service.generate_daily_plan(user_id=user.id)
        
        completed_task_id = tasks_with_priorities[4].id
        task_ids = [s.task_id for s in summaries]
        assert completed_task_id not in task_ids
    
    async def test_generate_daily_plan_summary_text_format(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        summaries = await service.generate_daily_plan(user_id=user.id)
        
        assert len(summaries) > 0
        for idx, summary in enumerate(summaries, 1):
            assert f"#{idx}" in summary.summary_text
            assert summary.summary_text != ""
    
    async def test_generate_daily_plan_only_once_per_day(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        summaries1 = await service.generate_daily_plan(user_id=user.id)
        summaries2 = await service.generate_daily_plan(user_id=user.id)
        
        assert len(summaries1) == len(summaries2)
        assert [s.id for s in summaries1] == [s.id for s in summaries2]
    
    async def test_generate_daily_plan_different_dates(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        summaries_today = await service.generate_daily_plan(
            user_id=user.id,
            target_date=today
        )
        
        summaries_tomorrow = await service.generate_daily_plan(
            user_id=user.id,
            target_date=tomorrow
        )
        
        assert len(summaries_today) > 0
        assert len(summaries_tomorrow) > 0
        assert [s.id for s in summaries_today] != [s.id for s in summaries_tomorrow]
    
    async def test_generate_daily_plan_with_no_tasks(
        self,
        test_db: AsyncSession,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        summaries = await service.generate_daily_plan(user_id=user.id)
        
        assert summaries == []
    
    async def test_get_today_plan_auto_generates_if_missing(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        summaries = await service.get_today_plan(user_id=user.id)
        
        assert len(summaries) > 0
        assert all(s.user_id == user.id for s in summaries)
    
    async def test_get_today_plan_returns_existing(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        summaries1 = await service.get_today_plan(user_id=user.id)
        summaries2 = await service.get_today_plan(user_id=user.id)
        
        assert [s.id for s in summaries1] == [s.id for s in summaries2]
    
    async def test_mark_task_complete(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        await service.generate_daily_plan(user_id=user.id)
        
        task_to_complete = tasks_with_priorities[0]
        
        completed_task = await service.mark_task_complete(
            task_id=task_to_complete.id,
            user_id=user.id,
            hours_worked=120
        )
        
        assert completed_task.status == "completed"
        assert completed_task.completed_at is not None
    
    async def test_mark_task_complete_updates_daily_summary(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        summaries = await service.generate_daily_plan(user_id=user.id)
        task_id = summaries[0].task_id
        
        await service.mark_task_complete(
            task_id=task_id,
            user_id=user.id,
            hours_worked=90
        )
        
        from sqlalchemy import select
        result = await test_db.execute(
            select(DailySummary).filter(DailySummary.task_id == task_id)
        )
        updated_summary = result.scalar_one()
        
        assert updated_summary.tasks_completed == 1
        assert updated_summary.hours_worked == 90
        assert "COMPLETED" in updated_summary.summary_text
    
    async def test_mark_task_complete_task_not_found(
        self,
        test_db: AsyncSession,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        with pytest.raises(ValueError, match="not found"):
            await service.mark_task_complete(
                task_id=99999,
                user_id=user.id
            )
    
    async def test_mark_task_complete_wrong_user(
        self,
        test_db: AsyncSession,
        user: User,
        project: Project
    ):
        other_user = User(
            email="other@example.com",
            username="otheruser",
            password_hash="hashed_password"
        )
        test_db.add(other_user)
        await test_db.commit()
        await test_db.refresh(other_user)
        
        task = Task(
            title="Task for other user",
            priority="medium",
            status="pending",
            project_id=project.id,
            assignee_id=other_user.id
        )
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)
        
        service = DailyPlanningService(test_db)
        
        with pytest.raises(ValueError, match="not assigned to user"):
            await service.mark_task_complete(
                task_id=task.id,
                user_id=user.id
            )
    
    async def test_get_plan_summary(
        self,
        test_db: AsyncSession,
        user: User,
        tasks_with_priorities: list
    ):
        service = DailyPlanningService(test_db)
        
        summaries = await service.generate_daily_plan(user_id=user.id)
        
        if summaries:
            await service.mark_task_complete(
                task_id=summaries[0].task_id,
                user_id=user.id,
                hours_worked=60
            )
        
        summary = await service.get_plan_summary(user_id=user.id, date=datetime.now())
        
        assert summary["total_tasks"] == len(summaries)
        assert summary["completed_tasks"] >= 1
        assert 0 <= summary["completion_rate"] <= 100
        assert summary["total_hours_worked"] >= 60
        assert len(summary["summaries"]) == len(summaries)
    
    async def test_get_plan_summary_no_tasks(
        self,
        test_db: AsyncSession,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        summary = await service.get_plan_summary(user_id=user.id, date=datetime.now())
        
        assert summary["total_tasks"] == 0
        assert summary["completed_tasks"] == 0
        assert summary["completion_rate"] == 0
        assert summary["total_hours_worked"] == 0
    
    async def test_priority_scoring_order(self, test_db: AsyncSession):
        service = DailyPlanningService(test_db)
        
        assert service.PRIORITY_SCORES['urgent'] > service.PRIORITY_SCORES['high']
        assert service.PRIORITY_SCORES['high'] > service.PRIORITY_SCORES['medium']
        assert service.PRIORITY_SCORES['medium'] > service.PRIORITY_SCORES['low']
    
    async def test_generate_summary_text_with_emojis(
        self,
        test_db: AsyncSession,
        project: Project,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        urgent_task = Task(
            title="Urgent task",
            priority="urgent",
            status="pending",
            project_id=project.id,
            assignee_id=user.id
        )
        
        summary_text = service._generate_summary_text(urgent_task, 1)
        
        assert "#1" in summary_text
        assert "🔥" in summary_text
        assert "Urgent task" in summary_text
    
    async def test_generate_summary_text_with_due_date(
        self,
        test_db: AsyncSession,
        project: Project,
        user: User
    ):
        service = DailyPlanningService(test_db)
        
        tomorrow = datetime.now() + timedelta(days=1)
        task = Task(
            title="Task due soon",
            priority="high",
            status="pending",
            project_id=project.id,
            assignee_id=user.id,
            due_date=tomorrow
        )
        
        summary_text = service._generate_summary_text(task, 1)
        
        assert "Due in 1 days" in summary_text or "Due in" in summary_text or "DUE" in summary_text or "OVERDUE" in summary_text
    
    async def test_select_top_three_tasks_respects_limit(
        self,
        test_db: AsyncSession,
        user: User,
        project: Project
    ):
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                priority="medium",
                status="pending",
                project_id=project.id,
                assignee_id=user.id
            )
            test_db.add(task)
        await test_db.commit()
        
        service = DailyPlanningService(test_db)
        top_tasks = await service._select_top_three_tasks(user.id, datetime.now())
        
        assert len(top_tasks) == 3
