"""drop_avatar

Revision ID: dc1aadf08b4d
Revises: 486e8c875e0b
Create Date: 2024-01-26 14:46:22.119614

"""

# revision identifiers, used by Alembic.
revision = "dc1aadf08b4d"
down_revision = "486e8c875e0b"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.drop_column("user", "avatar")


def downgrade():
    op.add_column("user", sa.Column("avatar", sa.Text(), nullable=True))
