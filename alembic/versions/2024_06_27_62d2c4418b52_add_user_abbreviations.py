"""Add user abbreviations

Revision ID: 62d2c4418b52
Revises: a8ae3ab67bc8
Create Date: 2024-06-27 15:55:45.434906

"""

# revision identifiers, used by Alembic.
revision = "62d2c4418b52"
down_revision = "a8ae3ab67bc8"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.add_column(table_name="user", column=sa.Column("abbreviation", sa.String(16), unique=True))


def downgrade():
    op.drop_column(table_name="user", column_name="abbreviation")
