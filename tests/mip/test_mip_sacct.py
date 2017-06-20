# -*- coding: utf-8 -*-
import datetime

import pytest

from trailblazer.mip import sacct


@pytest.mark.parametrize('time_str, expected_seconds', [
    ('02:53:08', (2 * 60 * 60) + (53 * 60)),
    ('3-07:13:56', (3 * 24 * 60 * 60) + (7 * 60 * 60) + (13 * 60)),
    ('18:47.020', (18 * 60)),
    ('00:00:35', 0)
])
def test_time_to_sec(time_str, expected_seconds):
    # GIVEN a time string
    # WHEN parsing it into number of seconds
    seconds = sacct.time_to_sec(time_str)
    # THEN it should match expected number of seconds (skipping individual secs)
    assert seconds == expected_seconds


@pytest.mark.parametrize('row, expected_job', [
    (['813887', 'gatk_genotypegvcfs_family_BOTH', 'prod001', 'core', '16', '10:03.096',
      '00:02:01', '2017-06-19T00:44:46', '2017-06-19T00:46:47', 'COMPLETED', '0:0'],
     dict(step='gatk_genotypegvcfs', context='family', is_completed=True)),
    (['815038', 'fastqc_ACC2698A3', 'prod001', 'core', '8', '00:00:00', '00:37:24',
      '2017-06-20T12:57:45', 'Unknown', 'RUNNING', '0:0'],
     dict(step='fastqc', context='ACC2698A3', is_completed=False)),
])
def test_convert_job(row, expected_job):
    # GIVEN a sacct row
    # WHEN parsing it for extracted data
    job = sacct.convert_job(row)
    # THEN it should have an integer for a job id
    assert isinstance(job['id'], int)
    # ... the step should be the job type
    assert job['step'] == expected_job['step']
    # ... the context should be the family/sample id
    assert job['context'] == expected_job['context']
    # ... it should be marked as completed only if that is the state
    assert job['is_completed'] == expected_job['is_completed']
    # ... the "start" should be a date
    assert isinstance(job['start'], datetime.datetime)
    # ... the "end" should be a date unless the job is "running"
    if job['state'] == 'RUNNING':
        assert job['end'] is None
    else:
        assert isinstance(job['end'], datetime.datetime)


def test_parse_sacct(files_raw):
    # GIVEN a sacct file with a number of row (1 header, rest jobs)
    lines = len(files_raw['sacct'])
    # WHEN parsing the sacct file
    jobs = sacct.parse_sacct(files_raw['sacct'])
    # THEN it should find all relevant rows
    assert len(jobs) == (lines - 1)


def test_filter_jobs(failed_sacct_jobs):
    # GIVEN a sacct output with COMPLETED, FAILED, and CANCELLED jobs
    completed_count = 17
    failed_count = 2
    cancelled_count = 34
    # WHEN filtering on "failed" jobs
    failed_jobs = sacct.filter_jobs(failed_sacct_jobs, failed=True)
    # THEN it should return jobs which are "failed" or "cancelled"
    assert len(failed_jobs) == (failed_count + cancelled_count)

    # WHEN filtering on "OK" jobs
    ok_jobs = sacct.filter_jobs(failed_sacct_jobs, failed=False)
    # THEN it should return jobs which are "completed"
    assert len(ok_jobs) == completed_count
