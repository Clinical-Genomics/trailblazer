"""Fix status spelling

Revision ID: 7e370bc3f587
Revises: 8a693bb99de3
Create Date: 2023-11-07 15:18:14.591783

"""

# revision identifiers, used by Alembic.
revision = "7e370bc3f587"
down_revision = "8a693bb99de3"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


OLD_OPTIONS = ("pending", "running", "completed", "failed", "error", "canceled", "completing", "qc")
NEW_OPTIONS = (
    "pending",
    "running",
    "completed",
    "failed",
    "error",
    "cancelled",
    "completing",
    "qc",
)


def upgrade():
    # Step 1: Allow both spellings for the transition
    temporary_options = OLD_OPTIONS + ("cancelled",)
    op.alter_column(
        "analysis",
        "status",
        existing_type=sa.Enum(*OLD_OPTIONS),
        type_=sa.Enum(*temporary_options),
        existing_nullable=True,
    )

    # Step 2: Data migration
    op.execute("UPDATE analysis SET status = 'cancelled' WHERE status = 'canceled'")

    # Step 3: Alter the column to only allow the new correct spelling
    op.alter_column(
        "analysis",
        "status",
        existing_type=sa.Enum(*temporary_options),
        type_=sa.Enum(*NEW_OPTIONS),
        existing_nullable=True,
    )


def downgrade():
    # Step 1: Allow both spellings for the transition
    temporary_options = OLD_OPTIONS + ("cancelled",)
    op.alter_column(
        "analysis",
        "status",
        existing_type=sa.Enum(*NEW_OPTIONS),
        type_=sa.Enum(*temporary_options),
        existing_nullable=True,
    )

    # Step 2: Data migration
    op.execute("UPDATE analysis SET status = 'canceled' WHERE status = 'cancelled'")

    # Step 3: Restore the column to only allow the old spelling
    op.alter_column(
        "analysis",
        "status",
        existing_type=sa.Enum(*temporary_options),
        type_=sa.Enum(*OLD_OPTIONS),
        existing_nullable=True,
    )
