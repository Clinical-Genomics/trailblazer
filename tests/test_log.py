# -*- coding: utf-8 -*-
import datetime
from pathlib import Path

import pytest

from trailblazer import log, exc
from trailblazer.log import LogAnalysis


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


def test_call(store, log_analysis, files):

    # GIVEN an empty store
    assert store.analyses().count() == 0

    # WHEN adding a new analysis log entry
    with Path(files['config']).open() as config_stream:
        new_run = log_analysis(config_stream, sampleinfo=files['sampleinfo'], sacct=files['sacct'])

    # THEN it should add the analysis log
    assert store.analyses(family=new_run.family).first() == new_run


def test_call_twice(store, log_analysis, files):
    # GIVEN an empty store
    assert store.analyses().count() == 0

    # WHEN adding a new analysis log entry twice
    with Path(files['config']).open() as config_stream:
        log_analysis(config_stream, sampleinfo=files['sampleinfo'], sacct=files['sacct'])
    first_analysis = store.analyses().first()
    with Path(files['config']).open() as config_stream:
        new_run = log_analysis(config_stream, sampleinfo=files['sampleinfo'], sacct=files['sacct'])

    # THEN it should skip adding the duplicate log to the database
    assert new_run is None
    assert store.analyses(family=first_analysis.family).count() == 1
    assert store.analyses(family=first_analysis.family).first() == first_analysis


def test_call_with_missing_files(log_analysis, files):
    # GIVEN missing sampleinfo and existing sacct
    config_path = Path(files['config'])
    sampleinfo_path = Path('/tmp/I_DO_NOT_EXIST.txt')
    sacct_path = Path(files['sacct'])
    assert sampleinfo_path.exists() is False
    assert sacct_path.exists() is True
    # WHEN calling the log analysis API
    # THEN it should raise an exception
    with pytest.raises(exc.MissingFileError):
        with config_path.open() as config_stream:
            log_analysis(config_stream, sampleinfo=sampleinfo_path, sacct=sacct_path)

    # GIVEN existing sampleinfo and missing sacct
    sampleinfo_path = Path(files['sampleinfo'])
    sacct_path = Path('/tmp/I_DO_NOT_EXIST.txt')
    assert sampleinfo_path.exists() is True
    assert sacct_path.exists() is False
    # WHEN calling the log analysis API
    # THEN it should also raise and exception
    with pytest.raises(exc.MissingFileError):
        with config_path.open() as config_stream:
            log_analysis(config_stream, sampleinfo=sampleinfo_path, sacct=sacct_path)


def test_parse_sacct(files_data):
    # GIVEN sacct jobs from a finished analysis
    sacct_jobs = files_data['sacct']
    analysis_end = datetime.datetime(2017, 6, 19, 3, 39, 56)
    # WHEN parsing them for info
    jobs_count = len(sacct_jobs)    # TODO: see code in _call_ in class LogAnalysis for proper
    # jobs_count calculation
    sacct_data, last_job_end = log.LogAnalysis._parse_sacct(sacct_jobs, jobs_count=jobs_count)
    # THEN it should return info about the jobs in general
    assert sacct_data['jobs'] == len(sacct_jobs)
    assert sacct_data['completed_jobs'] == len(sacct_jobs)
    # ... and correctly determine the end of the last job
    assert last_job_end == analysis_end


def test_parse_sacct_all_fails(allfailed_sacct_jobs):
    # GIVEN sacct jobs from analysis with all failed jobs
    # WHEN parsing out info
    sacct_data, last_job_end = log.LogAnalysis._parse_sacct(allfailed_sacct_jobs)
    # THEN the "analysis end" time should be unknown
    assert last_job_end is None


@pytest.mark.parametrize('analysis_types, expected_type', [
    (['wes'], 'wes'),                # single sample and analysis type
    (['wgs', 'wgs', 'wgs'], 'wgs'),  # multiple samples, single type
    (['wes', 'wgs', 'wgs'], 'wgs'),  # multiple samples, multiple types
])
def test_get_analysis_type(analysis_types, expected_type):
    # GIVEN a list of analysis types; wes, wgs, rna
    # WHEN determining the overall type
    analysis_type = log.LogAnalysis._get_analysis_type(analysis_types)
    # THEN it should be correct :-P
    assert analysis_type == expected_type


def test_parse(files_data):
    # GIVEN a finished analysis with all jobs completed
    config_data = files_data['config']
    sampleinfo_data = files_data['sampleinfo']
    sacct_jobs = files_data['sacct']
    # WHEN parsing log-information
    run_data = log.LogAnalysis.parse(config_data, sampleinfo_data, sacct_jobs, jobs=None)
    # THEN it should have parsed out a completed date
    assert run_data['status'] == 'completed'
    assert isinstance(run_data['completed_at'], datetime.datetime)
