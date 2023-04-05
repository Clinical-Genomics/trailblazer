"""Adds a use_tower column to allow tower support

Revision ID: ae1c26559e9b
Revises: fca618ecc3ad
Create Date: 2023-04-05 16:49:18.016810

"""

# revision identifiers, used by Alembic.
revision = "ae1c26559e9b"
down_revision = "fca618ecc3ad"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.add_column("analysis", sa.Column("use_tower", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("analysis", "use_tower")
