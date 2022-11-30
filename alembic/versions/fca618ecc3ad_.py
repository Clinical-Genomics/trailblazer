"""adds a uploaded at column when an analysis is uploaded to its corresponding place

Revision ID: fca618ecc3ad
Revises: 85f409b2eeeb
Create Date: 2022-11-30 10:58:36.190963

"""

# revision identifiers, used by Alembic.
revision = 'fca618ecc3ad'
down_revision = '85f409b2eeeb'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("analysis", sa.Column("uploaded_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("analysis", "uploaded_at")
