"""add another option for status field

Revision ID: afffbd40f0c3
Revises: 2029c2789209
Create Date: 2016-08-23 10:07:37.799154

"""

# revision identifiers, used by Alembic.
revision = "afffbd40f0c3"
down_revision = "2029c2789209"
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy import types

OLD_OPTIONS = ("pending", "running", "completed", "failed")
NEW_OPTIONS = ("pending", "running", "completed", "failed", "error")


def upgrade():
    op.alter_column(
        "analysis",
        "status",
        existing_type=types.Enum(*OLD_OPTIONS),
        type_=types.Enum(*NEW_OPTIONS),
    )


def downgrade():
    op.alter_column(
        "analysis",
        "status",
        existing_type=types.Enum(*NEW_OPTIONS),
        type_=types.Enum(*OLD_OPTIONS),
    )
