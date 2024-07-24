"""Make abbreviation non nullable

Revision ID: e0f217219a92
Revises: 8184202b1654
Create Date: 2024-07-24 13:11:21.535974

"""

# revision identifiers, used by Alembic.
revision = "e0f217219a92"
down_revision = "8184202b1654"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.alter_column("user", "abbreviation", existing_type=sa.String(length=32), nullable=False)


def downgrade():
    op.alter_column("user", "abbreviation", existing_type=sa.String(length=32), nullable=True)
