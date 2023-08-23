import datetime

import alchy
from sqlalchemy import Column, ForeignKey, UniqueConstraint, orm, types

from trailblazer.constants import (
    PRIORITY_OPTIONS,
    TYPES,
    SlurmJobStatus,
    TrailblazerStatus,
    WorkflowManager,
)

Model = alchy.make_declarative_base(Base=alchy.ModelBase)


class Info(Model):
    """Keep track of metadata."""

    __tablename__ = "info"

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, default=datetime.datetime.now)
    updated_at = Column(types.DateTime)


class User(Model):
    __tablename__ = "user"

    avatar = Column(types.Text)
    created_at = Column(types.DateTime, default=datetime.datetime.now)
    email = Column(types.String(128), unique=True)
    google_id = Column(types.String(128), unique=True)
    id = Column(types.Integer, primary_key=True)
    is_archived = Column(types.Boolean, default=False)
    name = Column(types.String(128))

    runs = orm.relationship("Analysis", backref="user")

    @property
    def first_name(self) -> str:
        """First part of name."""
        return self.name.split(" ")[0]

    def __str__(self) -> str:
        return self.name


class Analysis(Model):
    """Analysis record."""

    __tablename__ = "analysis"
    __table_args__ = (
        UniqueConstraint("family", "started_at", "status", name="_uc_family_start_status"),
    )

    id = Column(types.Integer, primary_key=True)
    family = Column(types.String(128), nullable=False)

    version = Column(types.String(32))
    logged_at = Column(types.DateTime, default=datetime.datetime.now)
    started_at = Column(types.DateTime)
    completed_at = Column(types.DateTime)
    status = Column(types.Enum(*TrailblazerStatus.statuses()))
    priority = Column(types.Enum(*PRIORITY_OPTIONS))
    out_dir = Column(types.Text)
    config_path = Column(types.Text)
    comment = Column(types.Text)
    is_deleted = Column(types.Boolean, default=False)
    is_visible = Column(types.Boolean, default=True)
    type = Column(types.Enum(*TYPES))
    user_id = Column(ForeignKey(User.id))
    progress = Column(types.Float, default=0.0)
    data_analysis = Column(types.String(32))
    ticket_id = Column(types.String(32))
    uploaded_at = Column(types.DateTime)
    workflow_manager = Column(
        types.Enum(*WorkflowManager.list()), default=WorkflowManager.SLURM.value
    )

    jobs = orm.relationship("Job", cascade="all,delete", backref="analysis")

    @property
    def has_ongoing_status(self) -> bool:
        """Check if analysis status is ongoing."""
        return self.status in TrailblazerStatus.ongoing_statuses()


class Job(Model):
    """Represent a step in the pipeline."""

    __tablename__ = "job"

    id = Column(types.Integer, primary_key=True)
    analysis_id = Column(ForeignKey(Analysis.id, ondelete="CASCADE"), nullable=False)
    slurm_id = Column(types.Integer)
    name = Column(types.String(64))
    context = Column(types.String(64))
    started_at = Column(types.DateTime)
    elapsed = Column(types.Integer)
    status = Column(types.Enum(*SlurmJobStatus.statuses()))
