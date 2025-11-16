"""Add accounts table

Revision ID: 4c2d8e5f6a1b
Revises: 3b1f9c1a5d7a
Create Date: 2025-11-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c2d8e5f6a1b'
down_revision = '3b1f9c1a5d7a'
branch_labels = None
depends_on = None


def upgrade():
    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('account_type', sa.Enum('CHECKING', 'SAVINGS', 'BUSINESS', 'INVESTMENT', name='accounttype'), nullable=False),
        sa.Column('account_number', sa.String(length=20), nullable=False),
        sa.Column('balance', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('account_number', name='uq_accounts_account_number'),
    )

    # Create indexes
    op.create_index('ix_accounts_user_id', 'accounts', ['user_id'], unique=False)
    op.create_index('ix_accounts_account_number', 'accounts', ['account_number'], unique=True)

    # Add account_id column to transaction_events table if it doesn't exist
    with op.batch_alter_table('transaction_events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('processed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.create_foreign_key('fk_transaction_events_account_id', 'accounts', ['account_id'], ['id'])

    # Create indexes for new columns
    op.create_index('ix_transaction_events_account_id', 'transaction_events', ['account_id'], unique=False)
    op.create_index('ix_transaction_events_status', 'transaction_events', ['status'], unique=False)

    # Set default status for existing records
    try:
        op.execute("UPDATE transaction_events SET status = 'COMPLETED' WHERE status IS NULL")
    except Exception:
        pass


def downgrade():
    # Drop indexes from transaction_events
    op.drop_index('ix_transaction_events_status', table_name='transaction_events')
    op.drop_index('ix_transaction_events_account_id', table_name='transaction_events')

    # Remove columns from transaction_events
    with op.batch_alter_table('transaction_events', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transaction_events_account_id', type_='foreignkey')
        batch_op.drop_column('description')
        batch_op.drop_column('processed_at')
        batch_op.drop_column('status')
        batch_op.drop_column('account_id')

    # Drop accounts indexes and table
    op.drop_index('ix_accounts_account_number', table_name='accounts')
    op.drop_index('ix_accounts_user_id', table_name='accounts')
    op.drop_table('accounts')

