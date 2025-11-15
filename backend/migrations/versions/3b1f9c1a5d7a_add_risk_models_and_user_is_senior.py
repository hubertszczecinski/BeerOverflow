"""Add is_senior to users and create risk tables

Revision ID: 3b1f9c1a5d7a
Revises: 2af22b119b47
Create Date: 2025-11-15 14:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b1f9c1a5d7a'
down_revision = '2af22b119b47'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_senior flag to users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_senior', sa.Boolean(), nullable=True))

    # Initialize existing rows to False (0) where NULL
    try:
        op.execute("UPDATE users SET is_senior = 0 WHERE is_senior IS NULL")
    except Exception:
        # Safe to ignore if table is empty or SQLite quirks
        pass

    # Create behavior_profiles table
    op.create_table(
        'behavior_profiles',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tx_count', sa.Integer(), nullable=True),
        sa.Column('amount_sum', sa.Float(), nullable=True),
        sa.Column('amount_sumsq', sa.Float(), nullable=True),
        sa.Column('channels', sa.Text(), nullable=True),
        sa.Column('locations', sa.Text(), nullable=True),
        sa.Column('recipients', sa.Text(), nullable=True),
        sa.Column('hours', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('user_id', name='uq_behavior_profiles_user_id'),
    )
    op.create_index('ix_behavior_profiles_user_id', 'behavior_profiles', ['user_id'], unique=True)

    # Create transaction_events table
    op.create_table(
        'transaction_events',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('channel', sa.String(length=32), nullable=False),
        sa.Column('recipient_id', sa.String(length=128), nullable=True),
        sa.Column('location', sa.String(length=128), nullable=True),
        sa.Column('balance_before', sa.Float(), nullable=True),
        sa.Column('balance_after', sa.Float(), nullable=True),
        sa.Column('raw', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('risk_local', sa.Float(), nullable=True),
        sa.Column('risk_global', sa.Float(), nullable=True),
        sa.Column('risk_combined', sa.Float(), nullable=True),
        sa.Column('flags', sa.Text(), nullable=True),
    )
    op.create_index('ix_transaction_events_user_id', 'transaction_events', ['user_id'], unique=False)
    op.create_index('ix_transaction_events_timestamp', 'transaction_events', ['timestamp'], unique=False)
    op.create_index('ix_transaction_events_user_time', 'transaction_events', ['user_id', 'timestamp'], unique=False)


def downgrade():
    # Drop transaction_events indexes and table
    with op.batch_alter_table('transaction_events', schema=None) as batch_op:
        pass
    op.drop_index('ix_transaction_events_user_time', table_name='transaction_events')
    op.drop_index('ix_transaction_events_timestamp', table_name='transaction_events')
    op.drop_index('ix_transaction_events_user_id', table_name='transaction_events')
    op.drop_table('transaction_events')

    # Drop behavior_profiles index and table
    op.drop_index('ix_behavior_profiles_user_id', table_name='behavior_profiles')
    op.drop_table('behavior_profiles')

    # Remove is_senior column from users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_senior')

