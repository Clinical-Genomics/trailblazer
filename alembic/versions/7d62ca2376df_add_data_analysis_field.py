"""empty message

Revision ID: 7d62ca2376df
Revises: 0829dd9c54d7
Create Date: 2020-10-22 11:33:34.572234

"""

# revision identifiers, used by Alembic.
revision = "7d62ca2376df"
down_revision = "84079287ee2f"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from sqlalchemy import types

from alembic import op

OLD_OPTIONS = ("wes", "wgs", "rna")
NEW_OPTIONS = ("wes", "wgs", "rna", "tgs", "other")


def upgrade():
    op.add_column("analysis", sa.Column("data_analysis", sa.String(32), nullable=True))
    op.alter_column(
        "analysis",
        "type",
        existing_type=types.Enum(*OLD_OPTIONS),
        type_=types.Enum(*NEW_OPTIONS),
    )


def downgrade():
    op.drop_column("analysis", "data_analysis")
    op.alter_column(
        "analysis",
        "type",
        existing_type=types.Enum(*NEW_OPTIONS),
        type_=types.Enum(*OLD_OPTIONS),
    )
