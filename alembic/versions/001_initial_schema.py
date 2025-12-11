"""Initial database schema with all models

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types first
    project_status = sa.Enum('active', 'completed', 'archived', name='project_status')
    project_status.create(op.get_bind())
    
    task_status = sa.Enum('pending', 'in_progress', 'completed', 'cancelled', name='task_status')
    task_status.create(op.get_bind())
    
    task_priority = sa.Enum('low', 'medium', 'high', 'urgent', name='task_priority')
    task_priority.create(op.get_bind())
    
    inbox_status = sa.Enum('unprocessed', 'processed', 'archived', name='inbox_status')
    inbox_status.create(op.get_bind())
    
    feedback_type = sa.Enum('user_input', 'system_output', 'improvement', name='feedback_type')
    feedback_type.create(op.get_bind())
    
    llm_call_status = sa.Enum('success', 'error', 'timeout', name='llm_call_status')
    llm_call_status.create(op.get_bind())
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for users
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create projects table
    op.create_table('projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', project_status, nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for projects
    op.create_index('idx_projects_owner_status', 'projects', ['owner_id', 'status'])
    
    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', task_status, nullable=True),
        sa.Column('priority', task_priority, nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('assignee_id', sa.Integer(), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for tasks
    op.create_index('idx_tasks_project_status', 'tasks', ['project_id', 'status'])
    op.create_index('idx_tasks_assignee_status', 'tasks', ['assignee_id', 'status'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    
    # Create inbox_items table
    op.create_table('inbox_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('status', inbox_status, nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for inbox_items
    op.create_index('idx_inbox_items_user_status', 'inbox_items', ['user_id', 'status'])
    op.create_index('idx_inbox_items_created_at', 'inbox_items', ['created_at'])
    
    # Create plan_versions table
    op.create_table('plan_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unique constraint for plan versions per project/task
    op.create_index('idx_plan_versions_project_version', 'plan_versions', ['project_id', 'version_number'])
    op.create_index('idx_plan_versions_task_version', 'plan_versions', ['task_id', 'version_number'])
    
    # Create feedback table
    op.create_table('feedback',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('feedback_type', feedback_type, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('plan_version_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['plan_version_id'], ['plan_versions.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for feedback
    op.create_index('idx_feedback_project_type', 'feedback', ['project_id', 'feedback_type'])
    op.create_index('idx_feedback_task_type', 'feedback', ['task_id', 'feedback_type'])
    op.create_index('idx_feedback_user_type', 'feedback', ['user_id', 'feedback_type'])
    op.create_index('idx_feedback_resolved', 'feedback', ['is_resolved'])
    
    # Create daily_summaries table
    op.create_table('daily_summaries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('tasks_completed', sa.Integer(), nullable=True),
        sa.Column('hours_worked', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for daily_summaries
    op.create_index('idx_daily_summaries_date', 'daily_summaries', ['date'])
    op.create_index('idx_daily_summaries_user_date', 'daily_summaries', ['user_id', 'date'])
    
    # Create llm_call_logs table
    op.create_table('llm_call_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Integer(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('status', llm_call_status, nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('extra_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for llm_call_logs
    op.create_index('idx_llm_call_logs_user', 'llm_call_logs', ['user_id'])
    op.create_index('idx_llm_call_logs_model', 'llm_call_logs', ['model_name'])
    op.create_index('idx_llm_call_logs_created_at', 'llm_call_logs', ['created_at'])
    op.create_index('idx_llm_call_logs_status', 'llm_call_logs', ['status'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('llm_call_logs')
    op.drop_table('daily_summaries')
    op.drop_table('feedback')
    op.drop_table('plan_versions')
    op.drop_table('inbox_items')
    op.drop_table('tasks')
    op.drop_table('projects')
    op.drop_table('users')
    
    # Drop ENUM types
    op.execute('DROP TYPE llm_call_status')
    op.execute('DROP TYPE feedback_type')
    op.execute('DROP TYPE inbox_status')
    op.execute('DROP TYPE task_priority')
    op.execute('DROP TYPE task_status')
    op.execute('DROP TYPE project_status')