"""Add upload jobs

Revision ID: 486e8c875e0b
Revises: 6c3da78d1af0
Create Date: 2024-01-25 10:15:59.984529

"""

# revision identifiers, used by Alembic.
revision = "486e8c875e0b"
down_revision = "6c3da78d1af0"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        table_name="job", column=sa.Column("upload_analysis_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        constraint_name="fk_job_upload_analysis_id_analysis",
        source_table="job",
        referent_table="analysis",
        local_cols=["upload_analysis_id"],
        remote_cols=["id"],
    )


def downgrade():
    op.drop_constraint("fk_job_upload_analysis_id_analysis", "job", type_="foreignkey")
    op.drop_column("job", "upload_analysis_id")
