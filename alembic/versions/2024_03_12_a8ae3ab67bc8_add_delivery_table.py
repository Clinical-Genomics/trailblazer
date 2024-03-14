"""Add delivery table

Revision ID: a8ae3ab67bc8
Revises: febdb4e78bb5
Create Date: 2024-03-12 13:54:57.421263

"""

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from alembic import op

# revision identifiers, used by Alembic.
revision = "a8ae3ab67bc8"
down_revision = "febdb4e78bb5"
branch_labels = None
depends_on = None


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
        sa.Column(
            "analysis_id",
            sa.ForeignKey(Analysis.id, ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("delivered_by", sa.ForeignKey(User.id), nullable=False),
        sa.Column("delivered_date", sa.Date, nullable=False),
    )


def downgrade():
    op.drop_table("delivery")
