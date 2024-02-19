import datetime

from sqlalchemy import Column, ForeignKey, UniqueConstraint, orm, types

from trailblazer.constants import (
    PRIORITY_OPTIONS,
    TYPES,
    JobType,
    SlurmJobStatus,
    TrailblazerStatus,
    WorkflowManager,
)
from trailblazer.store.database import Model


class Info(Model):
    """Keep track of metadata."""

    __tablename__ = "info"

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, default=datetime.datetime.now)
    updated_at = Column(types.DateTime)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the object."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class User(Model):
    __tablename__ = "user"

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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at,
            "is_archived": self.is_archived,
        }


class Analysis(Model):
    """Analysis record."""

    __tablename__ = "analysis"
    __table_args__ = (
        UniqueConstraint("case_id", "started_at", "status", name="_uc_case_id_start_status"),
    )

    case_id = Column(types.String(128), nullable=False)
    comment = Column(types.Text)
    completed_at = Column(types.DateTime)
    config_path = Column(types.Text)
    id = Column(types.Integer, primary_key=True)
    is_visible = Column(types.Boolean, default=True)
    logged_at = Column(types.DateTime, default=datetime.datetime.now)
    order_id = Column(types.Integer, index=True)
    out_dir = Column(types.Text)
    priority = Column(types.Enum(*PRIORITY_OPTIONS))
    progress = Column(types.Float, default=0.0)
    started_at = Column(types.DateTime)
    status = Column(types.Enum(*TrailblazerStatus.statuses()))
    ticket_id = Column(types.String(32))
    type = Column(types.Enum(*TYPES))
    uploaded_at = Column(types.DateTime)
    user_id = Column(ForeignKey(User.id))
    version = Column(types.String(32))
    workflow = Column(types.String(32))
    workflow_manager = Column(types.Enum(*WorkflowManager.list()), default=WorkflowManager.SLURM)

    jobs = orm.relationship("Job", cascade="all,delete", backref="analysis")

    @property
    def has_ongoing_status(self) -> bool:
        """Check if analysis status is ongoing."""
        return self.status in TrailblazerStatus.ongoing_statuses()

    @property
    def analysis_jobs(self) -> list["Job"]:
        """Return upload jobs."""
        return [job for job in self.jobs if job.job_type == JobType.ANALYSIS]

    @property
    def upload_jobs(self) -> list["Job"]:
        """Return upload jobs."""
        return [job for job in self.jobs if job.job_type == JobType.UPLOAD]

    def to_dict(self) -> dict:
        """Return a dictionary representation of the object."""
        return {
            "id": self.id,
            "case_id": self.case_id,
            "version": self.version,
            "logged_at": self.logged_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "priority": self.priority,
            "order_id": self.order_id,
            "out_dir": self.out_dir,
            "config_path": self.config_path,
            "comment": self.comment,
            "is_visible": self.is_visible,
            "type": self.type,
            "user_id": self.user_id,
            "progress": self.progress,
            "workflow": self.workflow,
            "ticket_id": self.ticket_id,
            "uploaded_at": self.uploaded_at,
            "workflow_manager": self.workflow_manager,
        }


class Job(Model):
    """Represent a step in the workflow."""

    __tablename__ = "job"

    id = Column(types.Integer, primary_key=True)
    analysis_id = Column(ForeignKey(Analysis.id, ondelete="CASCADE"), nullable=False)
    slurm_id = Column(types.Integer)
    name = Column(types.String(64))
    context = Column(types.String(64))
    started_at = Column(types.DateTime)
    elapsed = Column(types.Integer)
    status = Column(types.Enum(*SlurmJobStatus.statuses()))
    job_type = Column(types.Enum(*JobType.types()), default=JobType.ANALYSIS, nullable=False)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the object."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "slurm_id": self.slurm_id,
            "name": self.name,
            "context": self.context,
            "started_at": self.started_at,
            "elapsed": self.elapsed,
            "status": self.status,
        }
