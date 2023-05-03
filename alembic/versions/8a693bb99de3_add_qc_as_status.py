"""add qc as status

Revision ID: 8a693bb99de3
Revises: d1183a4d6d27
Create Date: 2023-05-03 10:55:35.883947

"""

# revision identifiers, used by Alembic.
revision = "8a693bb99de3"
down_revision = "d1183a4d6d27"
branch_labels = None
depends_on = None

from sqlalchemy import types

from alembic import op

OLD_OPTIONS = ("pending", "running", "completed", "failed", "error", "canceled", "completing")
NEW_OPTIONS = ("pending", "running", "completed", "failed", "error", "canceled", "completing", "qc")


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
