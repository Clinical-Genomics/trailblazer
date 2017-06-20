# -*- coding: utf-8 -*-
import datetime
from pathlib import Path

import pytest

from trailblazer import log


@pytest.mark.parametrize('kwargs, expected_status', [
    (dict(finished=False, failed_jobs=0), 'running'),
    (dict(finished=True, failed_jobs=0), 'completed'),
    (dict(finished=False, failed_jobs=3), 'failed'),
    (dict(finished=True, failed_jobs=3), 'completed'),  # allows override!
])
def test_get_status(kwargs, expected_status):
    # GIVEN the inputs of wheter the run is finished and how many jobs have failed
    # WHEN getting the run status...
    run_status = log.LogAnalysis.get_status(**kwargs)
    # THEN it should return the expected status
    assert run_status == expected_status


def test_commit(store, log_analysis):
    # GIVEN a store with a pending log for a family
    family_id = 'family'
    store.add_pending(family=family_id)
    assert store.analyses(family=family_id, status='pending').count() > 0
    assert store.analyses(family=family_id, status='completed').count() == 0
    # WHEN commiting a new analysis log entry
    new_run = store.Analysis(family=family_id, status='completed')
    log_analysis.commit(new_run)
    # THEN it should add the new run log
    assert store.analyses(family=family_id, status='completed').count() == 1
    # ... and remove the "pending" log entry(s)
    assert store.analyses(family=family_id, status='pending').count() == 0


def test_call(store, log_analysis, files):
    # GIVEN an empty store
    assert store.analyses().count() == 0
    # WHEN adding a new analysis log entry
    with Path(files['config']).open() as config_stream:
        new_run = log_analysis(config_stream, sampleinfo=files['sampleinfo'], sacct=files['sacct'])
    # THEN it should add the analysis log
    assert store.analyses(family=new_run.family).first() == new_run

    # WHEN logging the same run a second time
    assert store.analyses().count() == 1
    current_analysis = store.analyses().first()
    with Path(files['config']).open() as config_stream:
        new_run = log_analysis(config_stream, sampleinfo=files['sampleinfo'], sacct=files['sacct'])
    # THEN it should skip adding the duplicate log to the database
    assert new_run is None
    assert store.analyses(family=current_analysis.family).count() == 1
    assert store.analyses(family=current_analysis.family).first() == current_analysis


def test_parse_sacct(files_data):
    # GIVEN sacct jobs from a finished analysis
    sacct_jobs = files_data['sacct']
    analysis_end = datetime.datetime(2017, 6, 19, 3, 39, 56)
    # WHEN parsing them for info
    sacct_data, last_job_end = log.LogAnalysis._parse_sacct(sacct_jobs)
    # THEN it should return info about the jobs in general
    assert sacct_data['jobs'] == len(sacct_jobs)
    assert sacct_data['completed_jobs'] == len(sacct_jobs)
    # ... and correctly determine the end of the last job
    assert last_job_end == analysis_end
