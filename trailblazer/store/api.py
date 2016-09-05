# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from alchy import Manager

from .models import Analysis, Model, Metadata

log = logging.getLogger(__name__)


def connect(uri):
    log.debug('open connection to database: %s', uri)
    manager = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return manager


def case(case_id):
    """Return analysis entries with for a case."""
    query = (Analysis.query.filter_by(case_id=case_id)
                           .order_by(Analysis.logged_at.desc()))
    return query


def analyses(analysis_id=None, since=None, is_ready=False, status=None):
    """List added analyses."""
    query = Analysis.query.order_by(Analysis.logged_at.desc())

    if since:
        log.debug("filter entries on date: %s", since)
        query = query.filter(Analysis.started_at > since)

    if analysis_id:
        log.debug("filter entries on id pattern: %s", analysis_id)
        query = query.filter(Analysis.case_id.contains(analysis_id))

    if status:
        if isinstance(status, list):
            status_str = ', '.join(status)
            query = query.filter(Analysis.status.in_(status))
        else:
            status_str = status
            query = query.filter_by(status=status)
        log.debug("filter entries on status category: %s", status_str)

    if is_ready:
        query = query.filter_by(status='completed', is_deleted=False)

    return query


def track_update():
    """Update metadata record with new updated date."""
    metadata = Metadata.query.first()
    if metadata:
        metadata.updated_at = datetime.now()
