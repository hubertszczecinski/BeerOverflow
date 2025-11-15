"""Set is_senior default True and backfill existing users

Revision ID: 7d2fbbf4b123
Revises: 3b1f9c1a5d7a
Create Date: 2025-11-15 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d2fbbf4b123'
down_revision = '3b1f9c1a5d7a'
branch_labels = None
depends_on = None


def upgrade():
    # Set server default to TRUE so new users default to senior
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'is_senior',
            existing_type=sa.Boolean(),
            server_default=sa.true(),
            existing_nullable=True,
        )

    # Backfill existing rows to senior
    try:
        op.execute("UPDATE users SET is_senior = 1 WHERE is_senior IS NULL OR is_senior = 0")
    except Exception:
        # Safe to ignore on empty tables or incompatible dialects
        pass


def downgrade():
    # Revert server default to NULL (no default)
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'is_senior',
            existing_type=sa.Boolean(),
            server_default=None,
            existing_nullable=True,
        )

    # Optionally revert values to 0 (non-senior) for deterministic downgrade
    try:
        op.execute("UPDATE users SET is_senior = 0 WHERE is_senior IS NULL OR is_senior = 1")
    except Exception:
        pass

