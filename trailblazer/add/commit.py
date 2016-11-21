# -*- coding: utf-8 -*-
import logging

from trailblazer.store import api
from .utils import same_entry

log = logging.getLogger(__name__)


def commit_analysis(manager, new_entry, email=None):
    """Store new analysis in the database."""
    # look up previous runs for the same case
    old_runs = api.case(case_id=new_entry.case_id)
    latest_run = old_runs.first()
    if latest_run is None or not same_entry(latest_run, new_entry):
        if new_entry.status == 'completed':
            # set failed runs to not be visible in dashboard
            for old_run in old_runs:
                old_runs.is_visible = False
            manager.commit()

        # save the new entry to the database
        if latest_run and latest_run.status in ('running', 'pending'):
            # replace old temporary entries
            log.debug("deleting existing entry: %s", new_entry.case_id)
            latest_run.delete()
            manager.commit()

        if email:
            new_entry.user = api.user(email)
        manager.add_commit(new_entry)
        log.info("added new entry: {entry.case_id} - {entry.status}"
                 .format(entry=new_entry))
