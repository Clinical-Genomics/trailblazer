# -*- coding: utf-8 -*-
FINISHED_STATUSES = ('Finished', 'Archived', 'Archiving')


def same_entry(entry, other_entry):
    """Compare two analysis entries if they are the same."""
    statuses = set()
    steps = set()
    for aentry in [entry, other_entry]:
        steps.add('na' if aentry.failed_step is None else aentry.failed_step)
        # collapse into "failed" status
        statuses.add('failed' if aentry.status in ('error', 'canceled') else
                     aentry.status)

    if entry.case_id != other_entry.case_id:
        return False
    elif entry.started_at != other_entry.started_at:
        return False
    elif len(statuses) > 1:
        return False
    elif len(steps) > 1:
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
