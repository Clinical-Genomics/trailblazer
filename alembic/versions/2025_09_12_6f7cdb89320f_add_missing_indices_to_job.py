"""Add missing indices to job

Revision ID: 6f7cdb89320f
Revises: 2e86e302d6f7
Create Date: 2025-09-12 16:20:48.267635

"""

# revision identifiers, used by Alembic.
revision = "6f7cdb89320f"
down_revision = "2e86e302d6f7"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.create_index(index_name="job_type_index", table_name="job", columns=["job_type"])
    op.create_index(index_name="status_index", table_name="job", columns=["status"])


def downgrade():
    op.drop_index(index_name="status_index", table_name="status")
    op.drop_index(index_name="job_type_index", table_name="job")
