"""Add upload jobs

Revision ID: 486e8c875e0b
Revises: 6c3da78d1af0
Create Date: 2024-01-25 10:15:59.984529

"""

# revision identifiers, used by Alembic.
revision = "486e8c875e0b"
down_revision = "6c3da78d1af0"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

from trailblazer.constants import JobType


def upgrade():
    op.add_column(
        table_name="job",
        column=sa.Column(
            name="job_type",
            type_=sa.Enum(*JobType.types()),
            server_default=JobType.ANALYSIS,
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column(table_name="job", column_name="job_type")
