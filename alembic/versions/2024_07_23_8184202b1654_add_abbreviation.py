"""Add abbreviation

Revision ID: 8184202b1654
Revises: a8ae3ab67bc8
Create Date: 2024-07-23 16:12:47.581294

"""

# revision identifiers, used by Alembic.
revision = "8184202b1654"
down_revision = "a8ae3ab67bc8"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "user", sa.Column("abbreviation", sa.String(length=32), unique=True, nullable=True)
    )


def downgrade():
    op.drop_column("user", "abbreviation")
