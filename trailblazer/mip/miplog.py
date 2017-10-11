

def job_ids(log_stream):
    """Grep out all lines with scancel example."""
    id_rows = [line for line in log_stream if 'scancel' in line]
    jobs = [id_row.strip()[-7:-1] for id_row in id_rows]
    return jobs
