"""Add is_archived to user table

Revision ID: b0c0ce27e4bd
Revises: 7d62ca2376df
Create Date: 2021-09-08 17:23:57.193228

"""

# revision identifiers, used by Alembic.
revision = "b0c0ce27e4bd"
down_revision = "7d62ca2376df"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("user", sa.Column("is_archived", sa.Boolean(), nullable=False, default=False))


def downgrade():
    op.drop_column("user", "is_archived")
