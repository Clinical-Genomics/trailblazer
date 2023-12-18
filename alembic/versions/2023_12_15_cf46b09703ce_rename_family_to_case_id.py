"""rename_family_to_case_id

Revision ID: cf46b09703ce
Revises: 7e370bc3f587
Create Date: 2023-12-15 16:13:14.461760

"""

# revision identifiers, used by Alembic.
revision = "cf46b09703ce"
down_revision = "7e370bc3f587"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.alter_column(
        "analysis", "family", new_column_name="case_id", existing_type=sa.Integer()
    )  # Drop the unique constraint


def downgrade():
    op.alter_column("analysis", "case_id", new_column_name="family", existing_type=sa.Integer())
