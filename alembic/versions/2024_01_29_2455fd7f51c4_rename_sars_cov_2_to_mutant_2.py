"""rename_sars-cov-2_to_mutant_2

Revision ID: 2455fd7f51c4
Revises: dc1aadf08b4d
Create Date: 2024-01-29 16:26:01.232870

"""

from sqlalchemy import orm

from trailblazer.store.models import Analysis

# revision identifiers, used by Alembic.
revision = "2455fd7f51c4"
down_revision = "dc1aadf08b4d"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for analysis in session.query(Analysis).filter(Analysis.data_analysis == "sars-cov-2"):
        analysis.data_analysis = "mutant"

    session.commit()


def downgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for analysis in session.query(Analysis).filter(Analysis.data_analysis == "mutant"):
        analysis.data_analysis = "sars-cov-2"

    session.commit()
