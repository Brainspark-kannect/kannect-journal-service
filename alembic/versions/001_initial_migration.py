"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create tables if they don't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create journal_entries table if it doesn't exist
    if 'journal_entries' not in existing_tables:
        op.create_table(
            'journal_entries',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('sentiment_score', sa.Float(), nullable=True),
            sa.Column('sentiment_label', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=func.now(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_journal_entries_id'), 'journal_entries', ['id'], unique=False)

    # Create habits table if it doesn't exist
    if 'habits' not in existing_tables:
        op.create_table(
            'habits',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('frequency', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_habits_id'), 'habits', ['id'], unique=False)

    # Create habit_logs table if it doesn't exist
    if 'habit_logs' not in existing_tables:
        op.create_table(
            'habit_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('habit_id', sa.Integer(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), server_default=func.now(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_habit_logs_id'), 'habit_logs', ['id'], unique=False)

    # Create goals table if it doesn't exist
    if 'goals' not in existing_tables:
        op.create_table(
            'goals',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('title', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('due_date', sa.DateTime(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=func.now(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_goals_id'), 'goals', ['id'], unique=False)

def downgrade():
    # Only drop tables if they exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'goals' in existing_tables:
        op.drop_index(op.f('ix_goals_id'), table_name='goals')
        op.drop_table('goals')
    if 'habit_logs' in existing_tables:
        op.drop_index(op.f('ix_habit_logs_id'), table_name='habit_logs')
        op.drop_table('habit_logs')
    if 'habits' in existing_tables:
        op.drop_index(op.f('ix_habits_id'), table_name='habits')
        op.drop_table('habits')
    if 'journal_entries' in existing_tables:
        op.drop_index(op.f('ix_journal_entries_id'), table_name='journal_entries')
        op.drop_table('journal_entries') 