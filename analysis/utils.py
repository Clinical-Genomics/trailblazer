# -*- coding: utf-8 -*-
from datetime import datetime

from path import path

from analysis.exc import MultipleFilesError


def scan(root_dir):
    """Scan root for MIP analyses.

    Will look for qc sample info files.
    """
    files = path(root_dir).glob('**/**/**/*_sampleInfo.yaml')
    return files


def get_sacctout(analysis_root):
    """Return the path to the sacct STDOUT file."""
    files = path(analysis_root).glob('bwa/info/Sacct_*.stdout.txt')
    if len(files) > 1:
        raise MultipleFilesError(files)
    try:
        return files[0]
    except IndexError:
        # no file found - expect the analysis already is running
        return None


def analysis_status(sampleinfo_stream):
    """Check the QC sampleinfo file for the status of the analysis."""
    for line in sampleinfo_stream:
        clean_line = line.strip()
        if clean_line.startswith('AnalysisRunStatus'):
            status = clean_line.split(': ')[-1]
            return status


def inspect_error(sacct_stream):
    """Check STDOUT of the sacct command for failiures."""
    rows = [line.split() for line in sacct_stream]
    # filter rows that begin with a SLURM job id
    relevant_rows = [row for row in rows if row[0].isdigit()]
    # filter rows that have a FAILED status
    nonsuccess_rows = (row for row in relevant_rows if row[9] not in
                       ('COMPLETED', 'RUNNING'))
    # format the results
    nonsuccess_jobs = [convert_job(row) for row in nonsuccess_rows]
    return nonsuccess_jobs


def convert_job(row):
    """Convert sacct row to dict."""
    return {
        'id': row[0],
        'name': row[1],
        'time': row[6],
        'start': datetime.strptime(row[7], '%Y-%m-%dT%H:%M:%S'),
        'state': row[9]
    }
