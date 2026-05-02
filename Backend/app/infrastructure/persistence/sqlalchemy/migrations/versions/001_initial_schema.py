"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

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
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_created_at', 'users', ['created_at'])

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('salary_min', sa.Float(), nullable=True),
        sa.Column('salary_max', sa.Float(), nullable=True),
        sa.Column('salary_currency', sa.String(10), nullable=True),
        sa.Column('job_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('benefits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('source_url', sa.String(500), nullable=False),
        sa.Column('source_job_id', sa.String(255), nullable=True),
        sa.Column('posted_date', sa.DateTime(), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('company_logo_url', sa.String(500), nullable=True),
        sa.Column('company_website', sa.String(500), nullable=True),
        sa.Column('experience_level', sa.String(50), nullable=True),
        sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_remote', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('apply_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('scraped_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_url', name='uq_jobs_source_url')
    )
    op.create_index('idx_job_title', 'jobs', ['title'])
    op.create_index('idx_job_company', 'jobs', ['company'])
    op.create_index('idx_job_source', 'jobs', ['source'])
    op.create_index('idx_job_source_url', 'jobs', ['source_url'])
    op.create_index('idx_job_created_at', 'jobs', ['created_at'])
    op.create_index('idx_job_posted_date', 'jobs', ['posted_date'])

    # Create saved_jobs table
    op.create_table(
        'saved_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notes', sa.DateTime(), nullable=True),
        sa.Column('saved_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_job')
    )
    op.create_index('idx_saved_job_user_id', 'saved_jobs', ['user_id'])
    op.create_index('idx_saved_job_job_id', 'saved_jobs', ['job_id'])
    op.create_index('idx_saved_job_saved_at', 'saved_jobs', ['saved_at'])

    # Create search_history table
    op.create_table(
        'search_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('query', sa.String(500), nullable=False),
        sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('results_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('search_type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_search_history_user_id', 'search_history', ['user_id'])
    op.create_index('idx_search_history_job_id', 'search_history', ['job_id'])
    op.create_index('idx_search_history_created_at', 'search_history', ['created_at'])
    op.create_index('idx_search_history_query', 'search_history', ['query'])

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('query', sa.String(500), nullable=False),
        sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('frequency', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_triggered', sa.DateTime(), nullable=True),
        sa.Column('next_trigger', sa.DateTime(), nullable=True),
        sa.Column('notification_method', sa.String(50), nullable=False),
        sa.Column('new_jobs_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_alert_user_id', 'alerts', ['user_id'])
    op.create_index('idx_alert_is_active', 'alerts', ['is_active'])
    op.create_index('idx_alert_next_trigger', 'alerts', ['next_trigger'])
    op.create_index('idx_alert_created_at', 'alerts', ['created_at'])


def downgrade() -> None:
    op.drop_index('idx_alert_created_at', table_name='alerts')
    op.drop_index('idx_alert_next_trigger', table_name='alerts')
    op.drop_index('idx_alert_is_active', table_name='alerts')
    op.drop_index('idx_alert_user_id', table_name='alerts')
    op.drop_table('alerts')

    op.drop_index('idx_search_history_query', table_name='search_history')
    op.drop_index('idx_search_history_created_at', table_name='search_history')
    op.drop_index('idx_search_history_job_id', table_name='search_history')
    op.drop_index('idx_search_history_user_id', table_name='search_history')
    op.drop_table('search_history')

    op.drop_index('idx_saved_job_saved_at', table_name='saved_jobs')
    op.drop_index('idx_saved_job_job_id', table_name='saved_jobs')
    op.drop_index('idx_saved_job_user_id', table_name='saved_jobs')
    op.drop_table('saved_jobs')

    op.drop_index('idx_job_posted_date', table_name='jobs')
    op.drop_index('idx_job_created_at', table_name='jobs')
    op.drop_index('idx_job_source_url', table_name='jobs')
    op.drop_index('idx_job_source', table_name='jobs')
    op.drop_index('idx_job_company', table_name='jobs')
    op.drop_index('idx_job_title', table_name='jobs')
    op.drop_table('jobs')

    op.drop_index('idx_user_created_at', table_name='users')
    op.drop_index('idx_user_email', table_name='users')
    op.drop_table('users')
