"""initial_schema

Revision ID: ac7bf893a07b
Revises: 
Create Date: 2026-10-05 21:44:18.676569

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac7bf893a07b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial core tables: users, waste_reports, collection_requests."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    # 1. Users table
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False, unique=True, index=True),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('role', sa.String(length=20), nullable=False, server_default='user'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )

    # 2. WasteReports table
    if 'waste_reports' not in existing_tables:
        op.create_table(
            'waste_reports',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('image_path', sa.String(length=255), nullable=False),
            sa.Column('waste_type', sa.String(length=50), nullable=False),
            sa.Column('confidence', sa.Float(), nullable=False),
            sa.Column('disposal_guidance', sa.Text(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )

    # 3. CollectionRequests table
    if 'collection_requests' not in existing_tables:
        op.create_table(
            'collection_requests',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('waste_report_id', sa.Integer(), sa.ForeignKey('waste_reports.id', ondelete='SET NULL'), nullable=True, index=True),
            sa.Column('waste_type', sa.String(length=50), nullable=False),
            sa.Column('quantity', sa.String(length=100), nullable=True),
            sa.Column('location', sa.Text(), nullable=False),
            sa.Column('additional_notes', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=30), nullable=False, server_default='submitted'),
            sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    """Drop tables in reverse dependency order."""
    op.drop_table('collection_requests')
    op.drop_table('waste_reports')
    op.drop_table('users')
