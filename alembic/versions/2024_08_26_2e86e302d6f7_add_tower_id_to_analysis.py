"""Add tower id to analysis

Revision ID: 2e86e302d6f7
Revises: e0f217219a92
Create Date: 2024-08-26 12:50:57.070853

"""

# revision identifiers, used by Alembic.
revision = "2e86e302d6f7"
down_revision = "e0f217219a92"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column("analysis", sa.Column("tower_workflow_id", sa.String(length=32), nullable=True))


def downgrade():
    op.drop_column("analysis", "tower_workflow_id")
