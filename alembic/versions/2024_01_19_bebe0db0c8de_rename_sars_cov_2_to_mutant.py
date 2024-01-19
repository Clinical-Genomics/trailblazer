"""rename_sars-cov-2_to_mutant

Revision ID: bebe0db0c8de
Revises: 6c3da78d1af0
Create Date: 2024-01-19 11:36:22.328953

"""
from sqlalchemy import orm

from trailblazer.store.models import Analysis

# revision identifiers, used by Alembic.
revision = "bebe0db0c8de"
down_revision = "6c3da78d1af0"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for analysis in session.query(Analysis).filter(Analysis.data_analysis == "sars-cov-2"):
        print(f"Altering analysis: {str(analysis)}")
        analysis.data_analysis = "mutant"
        print(f"Altered analysis: {str(analysis)}")

    session.commit()


def downgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for analysis in session.query(Analysis).filter(Analysis.data_analysis == "mutant"):
        print(f"Altering analysis: {str(analysis)}")
        analysis.data_analysis = "sars-cov-2"
        print(f"Altered analysis: {str(analysis)}")

    session.commit()
