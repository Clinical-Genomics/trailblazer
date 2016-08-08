# -*- coding: utf-8 -*-
from trailblazer import utils


def test_convert_job():
    # GIVEN a row from Sacct output
    row = ['666784', 'ChanjoSexCheck_ADM1657A7', 'prod001', 'core', '1',
           '01:47.603', '00:02:16', '2016-08-03T08:38:36',
           '2016-08-03T08:40:52', 'COMPLETED', '0:0']
    # WHEN parsing data out of it
    data = utils.convert_job(row)
    # THEN it should return more structured
    assert data['id'] == row[0]
    assert data['name'] == row[1]


def test_scan(cust_root):
    # GIVEN a customer dir with some cases
    no_cases = len(cust_root['cases'])
    # WHEN scanning it for analyses
    files = utils.scan(cust_root['path'])
    # THEN it should return the expected number of files
    assert len(files) == no_cases
    for sampleinfo in files:
        # ... it should find sample info files
        assert sampleinfo.endswith('qc_sampleInfo.yaml')
        # ... it should correspond to the expted cases
        assert any(case_id in sampleinfo for case_id in cust_root['cases'])


def test_get_sacctout(analysis_multi, analysis_started, analysis_failed):
    # GIVEN an analysis which has been started multiple times
    root = analysis_multi['root']
    # WHEN getting the most relevant (latest) Sacct output
    sacct_out = utils.get_sacctout(root)
    # THEN it should return only the latest sacct output file
    assert sacct_out.endswith(analysis_multi['latest_sacct'])

    # GIVEN an analysis that has just started (no sacct output yet)
    root = analysis_started['root']
    # WHEN trying to look for the sacct output
    sacct_out = utils.get_sacctout(root)
    # THEN it should return None
    assert sacct_out is None

    # GIVEN an analysis that has failed on it's first run
    root = analysis_failed['root']
    family_id = analysis_failed['family_id']
    # WHEN trying to look for the sacct output
    sacct_out = utils.get_sacctout(root)
    # THEN it should return the (only) sacct out
    assert sacct_out.endswith("Sacct_{}.0.stdout.txt".format(family_id))


def test_inspect_error(sacct_failed):
    # GIVEN Sacct output with failed jobs
    # WHEN parsing the stream
    failed_jobs = utils.inspect_error(sacct_failed)
    # THEN it should return jobs with FAILED/CANCELLED status
    assert len(failed_jobs) >= 1
    for job in failed_jobs:
        assert job['state'] in ('FAILED', 'CANCELLED')
