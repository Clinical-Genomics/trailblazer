"""add new status option 'canceled'

Revision ID: 8786470f3a1b
Revises: 61df280b0af6
Create Date: 2016-10-10 11:02:26.762712

"""

# revision identifiers, used by Alembic.
revision = "8786470f3a1b"
down_revision = "61df280b0af6"
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy import types

OLD_OPTIONS = ("pending", "running", "completed", "failed", "error")
NEW_OPTIONS = ("pending", "running", "completed", "failed", "error", "canceled")


def upgrade():
    op.alter_column(
        "analysis", "status", existing_type=types.Enum(*OLD_OPTIONS), type_=types.Enum(*NEW_OPTIONS)
    )


def downgrade():
    op.alter_column(
        "analysis", "status", existing_type=types.Enum(*NEW_OPTIONS), type_=types.Enum(*OLD_OPTIONS)
    )
