# -*- coding: utf-8 -*-
from path import path

from trailblazer.store import Analysis
from .sacct import parse_sacct, get_analysistime, filter_failed
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
        with open(metadata['sacct_path'], 'r') as sacct_stream:
            sacct_jobs = parse_sacct(sacct_stream)
    status = determine_status(metadata['analysis_status'], sacct_jobs)
    metadata.update(status)
    new_entry = Analysis(**metadata)
    return new_entry


def determine_status(analysis_status, sacct_jobs):
    """Determine the status of an analysis."""
    if analysis_status in FINISHED_STATUSES:
        # calculate the total runtime
        runtime, cputime, completed_at = get_analysistime(sacct_jobs)
        status = dict(status='completed', runtime=runtime, cputime=cputime,
                      completed_at=completed_at)
    else:
        non_success = filter_failed(sacct_jobs)
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
    fam_key = sampleinfo.keys()[0]
    fam_data = sampleinfo[fam_key][fam_key]
    sample_ids = sampleinfo[fam_key].keys()
    sample_ids.remove(fam_key)
    analysis_start = fam_data['AnalysisDate']
    analysis_type = fam_data['AnalysisType']
    analysis_out = path(fam_data['Program']['QCCollect']['OutDirectory'])
    customer = fam_data['InstanceTag'][0]
    case_id = "{}-{}".format(customer, fam_key)
    cluster_const = analysis_out.parent.parent.parent
    config_path = cluster_const.joinpath(analysis_type, fam_key,
                                         "{}_config.yaml".format(fam_key))
    sacct_path = "{}.status".format(fam_data['lastLogFilePath'])
    values = {
        'case_id': case_id,
        'pipeline': 'mip',
        'pipeline_version': fam_data['MIPVersion'],
        'type': analysis_type,
        'root_dir': analysis_out.parent.parent,
        'started_at': analysis_start,
        'config_path': config_path,
        'samples': sample_ids,
        'analysis_status': fam_data['AnalysisRunStatus'],
        'sacct_path': sacct_path,
    }
    return values
