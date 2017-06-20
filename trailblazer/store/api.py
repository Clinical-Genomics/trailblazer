# -*- coding: utf-8 -*-
import datetime

import alchy

from . import models

TEMP_STATUSES = ('pending', 'running')


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

    def user(self, email):
        """Fetch a user from the database."""
        return self.User.query.filter_by(email=email).first()

    def find_analysis(self, family, started_at, status):
        """Find a single analysis."""
        query = self.Analysis.query.filter_by(family=family, started_at=started_at, status=status)
        return query.first()

    def analyses(self, family=None, status=None, deleted=None, temp=False):
        """Fetch analyses form the database."""
        query = self.Analysis.query.order_by(self.Analysis.started_at.desc())
        if family:
            query = query.filter_by(family=family)
        if status:
            query = query.filter_by(status=status)
        if isinstance(deleted, bool):
            query = query.filter_by(is_deleted=deleted)
        if temp:
            query = query.filter(self.Analysis.status.in_(TEMP_STATUSES))
        return query

    def analysis(self, analysis_id):
        """Get a single analysis."""
        return self.Analysis.query.get(analysis_id)

    def track_update(self):
        """Update metadata record with new updated date."""
        metadata = self.info()
        metadata.updated_at = datetime.datetime.now()
        self.commit()

    def is_running(self, family):
        """Check if an analysis is currently running/pending for a family."""
        latest_analysis = self.analyses(family=family).first()
        return latest_analysis and latest_analysis.status in TEMP_STATUSES

    def info(self):
        """Return metadata entry."""
        return self.Info.query.first()

    def add_pending(self, family, email=None):
        """Add pending entry for an analysis."""
        started_at = datetime.datetime.now()
        new_log = self.Analysis(family=family, status='pending', started_at=started_at)
        new_log.user = self.user(email) if email else None
        self.add_commit(new_log)
        return new_log


class Store(alchy.Manager, BaseHandler):

    def __init__(self, uri):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=models.Model)
