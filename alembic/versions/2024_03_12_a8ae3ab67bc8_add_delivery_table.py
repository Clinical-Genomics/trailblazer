"""Add delivery table

Revision ID: a8ae3ab67bc8
Revises: febdb4e78bb5
Create Date: 2024-03-12 13:54:57.421263

"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# revision identifiers, used by Alembic.
revision = "a8ae3ab67bc8"
down_revision = "febdb4e78bb5"
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analysis"

    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)


def upgrade():
    op.create_table(
        "delivery",
        sa.Column("id", sa.Uuid, nullable=False),
        sa.Column("analysis_id", sa.ForeignKey(Analysis.id, ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.ForeignKey(User.id), nullable=False),
        sa.Column("delivered_at", sa.DateTime, nullable=False),
    )


def downgrade():
    op.drop_table("delivery")
