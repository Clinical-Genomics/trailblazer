# -*- coding: utf-8 -*-
"""Store backend in Trailblazer"""
from typing import List
import datetime as dt
from pathlib import Path
import shutil

import alchy
import sqlalchemy as sqa
import ruamel

from trailblazer.constants import COMPLETED_STATUS, FAILED_STATUS, ONGOING_STATUSES
from trailblazer.store import models
from trailblazer.mip import files, trending


class BaseHandler:
    User = models.User
    Analysis = models.Analysis
    Job = models.Job
    Info = models.Info

    def setup(self):
        self.create_all()
        # add initial metadata record (for web interface)
        new_info = self.Info()
        self.add_commit(new_info)

    def find_analysis(self, family, started_at, status):
        """Find a single analysis."""
        query = self.Analysis.query.filter_by(family=family, started_at=started_at, status=status)
        return query.first()

    def find_analyses_with_comment(self, comment):
        """Find a analyses containing comment."""
        analysis_query = self.Analysis.query

        analysis_query = analysis_query.filter(self.Analysis.comment.like(f"%{comment}%"))
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
            analysis_query = analysis_query.filter(self.Analysis.status.in_(ONGOING_STATUSES))
        if before:
            analysis_query = analysis_query.filter(self.Analysis.started_at < before)
        if is_visible is not None:
            analysis_query = analysis_query.filter_by(is_visible=is_visible)
        return analysis_query.order_by(self.Analysis.started_at.desc())

    def analysis(self, analysis_id: int) -> models.Analysis:
        """Get a single analysis."""
        return self.Analysis.query.get(analysis_id)

    def track_update(self):
        """Update the latest updated date in the database."""
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
            self.Job.name.label("name"),
            sqa.func.count(self.Job.id).label("count"),
        ).filter(self.Job.status != "cancelled")

        if since_when:
            categories = categories.filter(self.Job.started_at > since_when)

        categories = categories.group_by(self.Job.name).all()

        data = [{"name": category.name, "count": category.count} for category in categories]
        return data

    def jobs(self):
        """Return all jobs in the database."""
        return self.Job.query

    # CG code

    def mark_analyses_deleted(self, case_id: str) -> None:
        """ mark analyses connected to a case as deleted """
        for old_analysis in self.analyses(family=case_id):
            old_analysis.is_deleted = True
        self.commit()

    # Duplicate/redundant needed for backwards compatibility for now
    def add_pending_analysis(self, case_id: str, email: str = None) -> None:
        """ Add analysis as pending"""
        self.add_pending(case_id, email)

    @staticmethod
    def get_sampleinfo(analysis: models.Analysis) -> str:
        """Get the sample info path for an analysis."""
        raw_data = ruamel.yaml.safe_load(Path(analysis.config_path).open())
        data = files.parse_config(raw_data)
        return data["sampleinfo_path"]

    @staticmethod
    def parse_qcmetrics(data: dict) -> dict:
        """Call internal Trailblazer MIP API."""
        return files.parse_qcmetrics(data)

    # Duplicate/redundant needed for backwards compatibility for now
    def is_analysis_ongoing(self, case_id: str) -> bool:
        """Call internal Trailblazer API"""
        return self.is_latest_analysis_ongoing(case_id=case_id)

    # Duplicate
    def is_analysis_failed(self, case_id: str) -> bool:
        """Call internal Trailblazer API"""
        return self.is_latest_analysis_failed(case_id=case_id)

    # Duplicate/redundant needed for backwards compatibility for now
    def is_analysis_completed(self, case_id: str) -> bool:
        """Call internal Trailblazer API"""
        return self.is_latest_analysis_completed(case_id=case_id)

    # Duplicate/redundant needed for backwards compatibility for now
    def get_analysis_status(self, case_id: str) -> str:
        """Call internal Trailblazer API"""
        return self.get_latest_analysis_status(case_id=case_id)

    def has_analysis_started(self, case_id: str) -> bool:
        """Check if analysis has started"""
        statuses = ("ongoing", "failed", "completed")
        get_analysis_status = {
            "ongoing": self.is_analysis_ongoing,
            "failed": self.is_analysis_failed,
            "completed": self.is_analysis_completed,
        }
        for status in statuses:
            has_started = get_analysis_status[status](case_id=case_id)
            if has_started:
                return has_started
        return False

    def delete_analysis(
        self,
        family: str,
        date: dt.datetime,
        yes: bool = False,
        dry_run: bool = False,
    ):
        """Delete the analysis output."""
        if self.analyses(family=family, temp=True).count() > 0:
            raise ValueError("analysis for family already running")
        analysis_obj = self.find_analysis(family, date, "completed")
        assert analysis_obj.is_deleted is False
        analysis_path = Path(analysis_obj.out_dir).parent

        if yes and not dry_run:
            shutil.rmtree(analysis_path, ignore_errors=True)
            analysis_obj.is_deleted = True
            self.commit()

    @staticmethod
    def get_trending(mip_config_raw: str, qcmetrics_raw: str, sampleinfo_raw: dict) -> dict:
        """Get trending data for a MIP analysis"""
        return trending.parse_mip_analysis(
            mip_config_raw=mip_config_raw,
            qcmetrics_raw=qcmetrics_raw,
            sampleinfo_raw=sampleinfo_raw,
        )

    def get_family_root_dir(self, family_id: str):
        """Get path for a case"""
        return Path(self.families_dir) / family_id

    def get_latest_logged_analysis(self, case_id: str):
        """Get the the analysis with the latest logged_at date"""
        return self.analyses(family=case_id).order_by(models.Analysis.logged_at.desc())

    @staticmethod
    def get_sampleinfo_date(data: dict) -> str:
        """Get date from a sampleinfo """
        return data["analysis_date"]


class Store(alchy.Manager, BaseHandler):
    def __init__(self, uri: str, families_dir: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=models.Model)
        self.families_dir = families_dir
