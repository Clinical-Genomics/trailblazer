"""drop_is_deleted

Revision ID: 6c3da78d1af0
Revises: cf46b09703ce
Create Date: 2023-12-28 10:56:38.228855

"""

# revision identifiers, used by Alembic.
revision = "6c3da78d1af0"
down_revision = "cf46b09703ce"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.drop_column("analysis", "is_deleted")


def downgrade():
    op.add_column("analysis", sa.Column("is_deleted", sa.Boolean(), nullable=True))
