"""add hold delivery functionality

Revision ID: f943917ee854
Revises: 6f7cdb89320f
Create Date: 2026-06-24 11:25:36.369802

"""

# revision identifiers, used by Alembic.
revision = "f943917ee854"
down_revision = "6f7cdb89320f"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        table_name="analysis",
        column=sa.Column("hold_delivery", sa.Boolean, nullable=False, default=False, index=True),
    )


def downgrade():
    op.drop_column(table_name="analysis", column_name="hold_delivery")
