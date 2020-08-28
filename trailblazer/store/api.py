# -*- coding: utf-8 -*-
from typing import List
import datetime as dt

import alchy
import sqlalchemy as sqa

from trailblazer.mip.config import ConfigHandler
from trailblazer.constants import COMPLETED_STATUS, FAILED_STATUS, ONGOING_STATUSES
from . import models


class BaseHandler:
    User = models.User
    Analysis = models.Analysis
    Job = models.Job
    Info = models.Info

    def setup(self):
        self.create_all()
        # add inital metadata record (for web interface)
        new_info = self.Info()
        self.add_commit(new_info)

    def find_analysis(self, family, started_at, status):
        """Find a single analysis."""
        query = self.Analysis.query.filter_by(
            family=family, started_at=started_at, status=status
        )
        return query.first()

    def find_analyses_with_comment(self, comment):
        """Find a analyses containing comment."""
        analysis_query = self.Analysis.query

        analysis_query = analysis_query.filter(
            self.Analysis.comment.like(f"%{comment}%")
        )
        return analysis_query

    def analyses(
        self,
        *,
        family: str = None,
        query: str = None,
        status: str = None,
        deleted: bool = None,
        temp: bool = False,
        before: dt.datetime = None,
        is_visible: bool = None,
    ):
        """Fetch analyses form the database."""
        analysis_query = self.Analysis.query
        if family:
            analysis_query = analysis_query.filter_by(family=family)
        elif query:
            analysis_query = analysis_query.filter(
                sqa.or_(
                    self.Analysis.family.like(f"%{query}%"),
                    self.Analysis.status.like(f"%{query}%"),
                )
            )
        if status:
            analysis_query = analysis_query.filter_by(status=status)
        if isinstance(deleted, bool):
            analysis_query = analysis_query.filter_by(is_deleted=deleted)
        if temp:
            analysis_query = analysis_query.filter(
                self.Analysis.status.in_(ONGOING_STATUSES)
            )
        if before:
            analysis_query = analysis_query.filter(self.Analysis.started_at < before)
        if is_visible is not None:
            analysis_query = analysis_query.filter_by(is_visible=is_visible)
        return analysis_query.order_by(self.Analysis.started_at.desc())

    def analysis(self, analysis_id: int) -> models.Analysis:
        """Get a single analysis."""
        return self.Analysis.query.get(analysis_id)

    def track_update(self):
        """Update the lastest updated date in the database."""
        metadata = self.info()
        metadata.updated_at = dt.datetime.now()
        self.commit()

    def is_latest_analysis_ongoing(self, case_id: str) -> bool:
        """Check if the latest analysis is ongoing for a case_id"""
        latest_analysis = self.analyses(family=case_id).first()
        if latest_analysis and latest_analysis.status in ONGOING_STATUSES:
            return True
        return False

    def is_latest_analysis_failed(self, case_id: str) -> bool:
        """Check if the latest analysis is failed for a case_id"""
        latest_analysis = self.analyses(family=case_id).first()
        if latest_analysis and latest_analysis.status == FAILED_STATUS:
            return True
        return False

    def get_latest_analysis_status(self, case_id: str) -> str:
        """Get latest analysis status for a case_id"""
        latest_analysis = self.analyses(family=case_id).first()
        return latest_analysis.status

    def is_latest_analysis_completed(self, case_id: str) -> bool:
        """Check if the latest analysis is completed for a case_id"""
        latest_analysis = self.analyses(family=case_id).first()
        if latest_analysis and latest_analysis.status == COMPLETED_STATUS:
            return True
        return False

    def info(self) -> models.Info:
        """Return metadata entry."""
        return self.Info.query.first()

    def add_pending(self, family: str, email: str = None) -> models.Analysis:
        """Add pending entry for an analysis."""
        started_at = dt.datetime.now()
        new_log = self.Analysis(family=family, status="pending", started_at=started_at)
        new_log.user = self.user(email) if email else None
        self.add_commit(new_log)
        return new_log

    def add_user(self, name: str, email: str) -> models.User:
        """Add a new user to the database."""
        new_user = self.User(name=name, email=email)
        self.add_commit(new_user)
        return new_user

    def user(self, email: str) -> models.User:
        """Fetch a user from the database."""
        return self.User.query.filter_by(email=email).first()

    def aggregate_failed(self, since_when: dt.date = None) -> List:
        """Count the number of failed jobs per category (name)."""

        categories = self.session.query(
            self.Job.name.label("name"), sqa.func.count(self.Job.id).label("count")
        ).filter(self.Job.status != "cancelled")

        if since_when:
            categories = categories.filter(self.Job.started_at > since_when)

        categories = categories.group_by(self.Job.name).all()

        data = [
            {"name": category.name, "count": category.count} for category in categories
        ]
        return data

    def jobs(self):
        """Return all jobs in the database."""
        return self.Job.query


class Store(alchy.Manager, BaseHandler, ConfigHandler):
    def __init__(self, uri: str, families_dir: str):
        super(Store, self).__init__(
            config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=models.Model
        )
        self.families_dir = families_dir
