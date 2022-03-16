"""add express qos

Revision ID: 70b9d03a7e7f
Revises: b0c0ce27e4bd
Create Date: 2022-03-16 13:11:21.218493

"""

# revision identifiers, used by Alembic.
revision = "70b9d03a7e7f"
down_revision = "b0c0ce27e4bd"
branch_labels = None
depends_on = None

from alembic import op

from sqlalchemy import types

OLD_OPTIONS = ("low", "normal", "high")
NEW_OPTIONS = ("low", "normal", "high", "express")


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
