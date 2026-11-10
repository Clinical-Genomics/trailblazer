"""add workblock configuration

Revision ID: 638fe1e77287
Revises: f943917ee854
Create Date: 2026-11-09 16:01:23.970638

"""

# revision identifiers, used by Alembic.
revision = "638fe1e77287"
down_revision = "f943917ee854"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    table = op.create_table(
        "workblock_configuration",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("workblocks", sa.JSON, nullable=False),
    )

    op.bulk_insert(
        table,
        [
            {
                "id": 1,
                "version": 1,
                "workblocks": [
                    {
                        "id": "workblock-1",
                        "name": "Workblock 1",
                        "color": "#8dd909",
                        "workflows": [
                            "raredisease",
                            "nallo",
                            "mip-dna",
                            "mip-rna",
                            "tomte",
                            "fluffy",
                        ],
                    },
                    {
                        "id": "workblock-2",
                        "name": "Workblock 2",
                        "color": "#d57012",
                        "workflows": [
                            "balsamic",
                            "rnafusion",
                            "raw-data",
                            "microsalt",
                            "mutant",
                            "taxprofiler",
                            "demultiplex",
                        ],
                    },
                ],
            }
        ],
    )


def downgrade():
    op.drop_table("workblock_configuration")
