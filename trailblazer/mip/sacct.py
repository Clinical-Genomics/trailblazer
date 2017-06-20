# -*- coding: utf-8 -*-
from datetime import datetime

NORMAL_CATEGORIES = ('COMPLETED', 'RUNNING', 'PENDING')
FAILED_CATEGORIES = ('FAILED', 'CANCELLED', 'TIMEOUT')
CATEGORIES = NORMAL_CATEGORIES + FAILED_CATEGORIES


def time_to_sec(time_str: str) -> int:
    """Convert time in string format to seconds.

    Skipping seconds since sometimes the last column is truncated
    for entries where >10 days.
    """
    total_sec = 0
    if '-' in time_str:
        # parse out days
        days, time_str = time_str.split('-')
        total_sec += (int(days) * 24 * 60 * 60)

    # parse out the hours and mins (skip seconds)
    hours_min_raw = time_str.split(':')[:-1]
    time_parts = [int(round(float(val))) for val in hours_min_raw]
    total_sec += time_parts[-1] * 60              # minutes
    if len(time_parts) > 1:
        total_sec += time_parts[-2] * 60 * 60     # hours
    return total_sec


def convert_job(row: list) -> dict:
    """Convert sacct row to dict."""
    state = row[-2]
    start_time_raw = row[-4]
    end_time_raw = row[-3]
    if state not in ('PENDING', 'CANCELLED'):
        start_time = datetime.strptime(start_time_raw, '%Y-%m-%dT%H:%M:%S')
        if state != 'RUNNING':
            end_time = datetime.strptime(end_time_raw, '%Y-%m-%dT%H:%M:%S')
        else:
            end_time = None
    else:
        start_time = end_time = None

    # parse name of job
    job_name = row[1]
    step_name, step_context = job_name.rstrip('_BOTH').rstrip('_SV').rsplit('_', 1)

    return {
        'id': int(row[0]),
        'name': job_name,
        'step': step_name,
        'context': step_context,
        'state': state,
        'start': start_time,
        'end': end_time,
        'elapsed': time_to_sec(row[-5]),
        'cpu': time_to_sec(row[-6]),
        'is_completed': state == 'COMPLETED',
    }


def parse_sacct(sacct_stream):
    """Parse out information from sacct status output."""
    rows = (line.split() for line in sacct_stream)
    # filter rows that begin with a SLURM job id
    relevant_rows = (row for row in rows if row[0].isdigit())
    jobs = [convert_job(row) for row in relevant_rows]
    return jobs


def filter_jobs(sacct_jobs, failed=True):
    """Filter jobs that have a FAILED etc. status."""
    categories = FAILED_CATEGORIES if failed else NORMAL_CATEGORIES
    filtered_jobs = [job for job in sacct_jobs if job['state'] in categories]
    return filtered_jobs
