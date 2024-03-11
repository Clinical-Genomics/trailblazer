"""Add refresh token column

Revision ID: febdb4e78bb5
Revises: e907e651fb9e
Create Date: 2024-03-08 10:38:28.151275

"""

# revision identifiers, used by Alembic.
revision = "febdb4e78bb5"
down_revision = "e907e651fb9e"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("user", sa.Column("refresh_token", sa.Text, nullable=True))

def downgrade():
    op.drop_column("user", "refresh_token")
