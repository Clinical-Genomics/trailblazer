"""empty message

Revision ID: 85f409b2eeeb
Revises: dd72c72e23a2
Create Date: 2022-11-11 11:27:17.102596

"""

# revision identifiers, used by Alembic.
revision = "85f409b2eeeb"
down_revision = "dd72c72e23a2"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("analysis", sa.Column("ticket_id", sa.String(32), nullable=True))


def downgrade():
    op.drop_column("analysis", "ticket_id")
