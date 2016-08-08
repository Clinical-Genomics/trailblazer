# -*- coding: utf-8 -*-
import logging

from alchy import Manager

from .models import Analysis, Model

log = logging.getLogger(__name__)


def connect(uri):
    log.debug('open connection to database: %s', uri)
    manager = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return manager


def analyses(analysis_id=None, since=None, is_ready=False):
    """List added analyses."""
    query = Analysis.query.order_by(Analysis.started_at.desc())

    if since:
        log.debug("filter analyses on date: %s", since)
        query = query.filter(Analysis.started_at > since)

    if analysis_id:
        log.debug("filter analyses on id pattern: %s", analysis_id)
        query = query.filter(Analysis.case_id.contains(analysis_id))

    if is_ready:
        query = query.filter_by(status='completed', is_deleted=False)

    return query
