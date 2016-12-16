# -*- coding: utf-8 -*-
from path import path
import yaml

from trailblazer.store import Analysis
from trailblazer.exc import MissingFileError
from .sacct import parse_sacct, get_analysistime, filter_jobs
from .utils import FINISHED_STATUSES


def build_entry(sampleinfo, sacct_stream=None):
    """Build analysis status entry from sampleinfo data.

    Doesn't require any database connection.
    """
    metadata = parse_sampleinfo(sampleinfo)
    if sacct_stream:
        sacct_jobs = parse_sacct(sacct_stream)
    else:
        # try with automatically detected file
        sacct_path = path(metadata['sacct_path'])
        if not sacct_path.exists():
            raise MissingFileError(sacct_path)
        with sacct_path.open('r') as sacct_stream:
            sacct_jobs = parse_sacct(sacct_stream)
    status = determine_status(metadata['analysis_status'], sacct_jobs)
    metadata.update(status)
    new_entry = Analysis(**metadata)
    return new_entry


def determine_status(analysis_status, sacct_jobs):
    """Determine the status of an analysis."""
    if analysis_status in FINISHED_STATUSES:
        # calculate the total runtime
        # finished status should override all else;
        # do our best to figure out runtime etc.
        success_jobs = filter_jobs(sacct_jobs, failed=False)
        runtime, cputime, completed_at = get_analysistime(success_jobs)
        status = dict(status='completed', runtime=runtime, cputime=cputime,
                      completed_at=completed_at)
    else:
        non_success = filter_jobs(sacct_jobs, failed=True)
        if len(non_success) == 0:
            status = dict(status='running')
        else:
            failed_step = non_success[0]['name']
            failed_at = non_success[0]['end']
            status = dict(status='failed', failed_step=failed_step,
                          failed_at=failed_at)
    return status


def parse_sampleinfo(sampleinfo):
    """Extract basic info from loaded sampleinfo file.

    Args:
        sampleinfo (dict): loaded contents from sampleinfo file

    Returns:
        dict: extracted and transformed values from sampleinfo
    """
    with open(sampleinfo['pedigree_file']['path'], 'r') as in_handle:
        ped_data = yaml.load(in_handle)
    fam_key = ped_data['family']
    sample_ids = sampleinfo['sample'].keys()
    analysis_types = set(sampleinfo['analysis_type'].values())
    # choose collapsed analysis type unless multiple - then assume wgs!
    analysis_type_raw = (analysis_types.pop() if len(analysis_types) == 1 else
                         'wgs')
    analysis_type = 'exomes' if analysis_type_raw == 'wes' else 'genomes'
    analysis_start = sampleinfo['analysis_date']
    analysis_out = path(sampleinfo['log_file_dir']).parent
    customer = ped_data['owner']
    case_id = "{}-{}".format(customer, fam_key)
    config_path = analysis_out.joinpath("{}_config.yaml".format(fam_key))
    sacct_path = "{}.status".format(sampleinfo['last_log_file_path'])
    values = {
        'case_id': case_id,
        'pipeline': 'mip',
        'pipeline_version': sampleinfo['mip_version'],
        'root_dir': analysis_out,
        'started_at': analysis_start,
        'config_path': config_path,
        'samples': sample_ids,
        'type': analysis_type,
        'analysis_status': sampleinfo['analysisrunstatus'],
        'sacct_path': sacct_path,
    }
    return values
