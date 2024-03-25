"""Make delivery fields nullable

Revision ID: a6a826d2cdc4
Revises: a8ae3ab67bc8
Create Date: 2024-03-21 14:22:57.012567

"""

# revision identifiers, used by Alembic.
revision = "a6a826d2cdc4"
down_revision = "a8ae3ab67bc8"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.alter_column("delivery", "delivered_by", existing_type=sa.Integer, nullable=True)
    op.alter_column(
        "delivery",
        "delivered_date",
        existing_type=sa.Date,
        new_column_name="delivered_at",
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "delivery",
        "delivered_at",
        existing_type=sa.Date,
        new_column_name="delivered_date",
        nullable=False,
    )
    op.alter_column("delivery", "delivered_by", existing_type=sa.Integer, nullable=False)
