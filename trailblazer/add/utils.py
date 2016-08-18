# -*- coding: utf-8 -*-
FINISHED_STATUSES = ('Finished', 'Archived', 'Archiving')


def same_entry(entry, other_entry):
    """Compare two analysis entries if they are the same."""
    for aentry in [entry, other_entry]:
        if aentry.failed_step is None:
            aentry.failed_step = 'na'

    if entry.case_id != other_entry.case_id:
        return False
    elif entry.started_at != other_entry.started_at:
        return False
    elif entry.status != other_entry.status:
        return False
    elif entry.failed_step != other_entry.failed_step:
        return False
    elif entry.failed_at != other_entry.failed_at:
        return False
    else:
        return True


def is_latest_mip(sampleinfo):
    """Check if the analysis is up to date."""
    fam_key = sampleinfo.keys()[0]
    version = sampleinfo[fam_key][fam_key].get('MIPVersion')
    return version is not None and version.startswith('v3.')
