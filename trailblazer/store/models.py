# -*- coding: utf-8 -*-
import datetime

import alchy
from sqlalchemy import Column, ForeignKey, orm, types, UniqueConstraint

from trailblazer.constants import (
    ONGOING_STATUSES,
    STATUS_OPTIONS,
    JOB_STATUS_OPTIONS,
    PRIORITY_OPTIONS,
    TYPES,
)


Model = alchy.make_declarative_base(Base=alchy.ModelBase)


class Info(Model):

    """Keep track of meta data."""

    __tablename__ = "info"

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, default=datetime.datetime.now)
    updated_at = Column(types.DateTime)


class User(Model):

    __tablename__ = "user"

    id = Column(types.Integer, primary_key=True)
    google_id = Column(types.String(128), unique=True)
    email = Column(types.String(128), unique=True)
    name = Column(types.String(128))
    avatar = Column(types.Text)
    created_at = Column(types.DateTime, default=datetime.datetime.now)

    runs = orm.relationship("Analysis", backref="user")

    @property
    def first_name(self) -> str:
        """First part of name."""
        return self.name.split(" ")[0]


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
    status = Column(types.Enum(*STATUS_OPTIONS))
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

    failed_jobs = orm.relationship("Job", backref="analysis")

    @property
    def has_ongoing_status(self):
        """Check if the log has an ongoing status: 'running|'pending'"""
        return self.status in ONGOING_STATUSES


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
    status = Column(types.Enum(*JOB_STATUS_OPTIONS))
