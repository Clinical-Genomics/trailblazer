"""Add order to analysis

Revision ID: 4b925b29ac45
Revises: 2455fd7f51c4
Create Date: 2024-02-02 13:22:01.439426

"""

# revision identifiers, used by Alembic.
revision = '4b925b29ac45'
down_revision = '2455fd7f51c4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(table_name="analysis", column=sa.Column(name="order_id", type_=sa.Integer, index=True))


def downgrade():
    op.drop_column(table_name="analysis", column_name="order_id")
