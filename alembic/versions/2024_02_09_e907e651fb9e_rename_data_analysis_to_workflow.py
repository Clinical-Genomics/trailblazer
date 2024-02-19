"""rename_data_analysis_to_workflow

Revision ID: e907e651fb9e
Revises: 4b925b29ac45
Create Date: 2024-02-09 16:45:01.272807

"""

# revision identifiers, used by Alembic.
revision = "e907e651fb9e"
down_revision = "4b925b29ac45"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.alter_column(
        "analysis", "data_analysis", new_column_name="workflow", existing_type=sa.String(32)
    )  # Drop the unique constraint


def downgrade():
    op.alter_column(
        "analysis", "workflow", new_column_name="data_analysis", existing_type=sa.String(32)
    )
