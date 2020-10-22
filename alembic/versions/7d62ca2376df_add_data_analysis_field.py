"""empty message

Revision ID: 7d62ca2376df
Revises: 0829dd9c54d7
Create Date: 2020-10-22 11:33:34.572234

"""

# revision identifiers, used by Alembic.
revision = "7d62ca2376df"
down_revision = "0829dd9c54d7"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("analysis", sa.Column("data_analysis", sa.String(), nullable=True))


def downgrade():
    op.drop_column("analysis", "data_analysis")
