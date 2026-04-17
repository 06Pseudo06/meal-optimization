"""add weight goal

Revision ID: c0a8f9c1e149
Revises: b31a18fc90e4
Create Date: 2026-04-03 12:11:13.150606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0a8f9c1e149'
down_revision: Union[str, Sequence[str], None] = 'b31a18fc90e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('weight_goal', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('current_weight', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'weight_goal')
    op.drop_column('users', 'current_weight')
