"""add qos maintenance

Revision ID: dd72c72e23a2
Revises: 70b9d03a7e7f
Create Date: 2022-10-05 12:24:03.517390

"""

# revision identifiers, used by Alembic.
revision = "dd72c72e23a2"
down_revision = "70b9d03a7e7f"
branch_labels = None
depends_on = None

from alembic import op

from sqlalchemy import types

OLD_OPTIONS = ("low", "normal", "high", "express")
NEW_OPTIONS = ("low", "normal", "high", "express", "maintenance")


def upgrade():
    op.alter_column(
        "analysis",
        "priority",
        existing_type=types.Enum(*OLD_OPTIONS),
        type_=types.Enum(*NEW_OPTIONS),
    )


def downgrade():
    op.alter_column(
        "analysis",
        "priority",
        existing_type=types.Enum(*NEW_OPTIONS),
        type_=types.Enum(*OLD_OPTIONS),
    )
