"""Add wts to data analysis

Revision ID: d1183a4d6d27
Revises: ae1c26559e9b
Create Date: 2023-04-19 17:54:51.611506

"""

# revision identifiers, used by Alembic.
revision = "d1183a4d6d27"
down_revision = "ae1c26559e9b"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from sqlalchemy import types

from alembic import op

OLD_OPTIONS = ("wes", "wgs", "rna", "tgs", "other")
NEW_OPTIONS = ("wes", "wgs", "rna", "tgs", "other", "wts")


def upgrade():
    op.alter_column(
        "analysis",
        "type",
        existing_type=types.Enum(*OLD_OPTIONS),
        type_=types.Enum(*NEW_OPTIONS),
    )


def downgrade():
    op.alter_column(
        "analysis",
        "type",
        existing_type=types.Enum(*NEW_OPTIONS),
        type_=types.Enum(*OLD_OPTIONS),
    )
