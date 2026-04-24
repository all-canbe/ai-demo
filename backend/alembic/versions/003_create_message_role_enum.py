"""create message role enum type

Revision ID: 003
Revises: 002
Create Date: 2026-04-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE messagerole AS ENUM ('USER', 'ASSISTANT')")
    op.execute("ALTER TABLE chat_messages ALTER COLUMN role TYPE messagerole USING role::messagerole")


def downgrade() -> None:
    pass
