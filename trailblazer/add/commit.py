# -*- coding: utf-8 -*-
import logging

from trailblazer.store import api
from .utils import same_entry

log = logging.getLogger(__name__)


def commit_analysis(manager, new_entry):
    """Store new analysis in the database."""
    # look up previous analyses for the same case
    old_entry = api.case(case_id=new_entry.case_id).first()
    if old_entry is None or not same_entry(old_entry, new_entry):
        # save the new entry to the database
        if old_entry and old_entry.status in ('running', 'pending'):
            # replace old temporary entries
            log.debug("deleting existing entry: %s", new_entry.case_id)
            old_entry.delete()
            manager.commit()

        manager.add_commit(new_entry)
        log.info("added new entry: {entry.case_id} - {entry.status}"
                 .format(entry=new_entry))
