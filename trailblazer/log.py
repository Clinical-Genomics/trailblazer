# -*- coding: utf-8 -*-
import logging
from pathlib import Path

import ruamel.yaml

from trailblazer.mip import sacct as sacct_api, files as files_api
from trailblazer.store import Store

log = logging.getLogger(__name__)


class LogAnalysis(object):

    def __init__(self, store: Store):
        self.store = store

    def __call__(self, config_stream, sampleinfo=None, sacct=None):
        """Add a new analysis log."""
        config_raw = ruamel.yaml.safe_load(config_stream)
        config_data = files_api.parse_config(config_raw)
        with open(sampleinfo or config_data['sample_info']) as stream:
            sampleinfo_raw = ruamel.yaml.safe_load(stream)
        sampleinfo_data = files_api.parse_sampleinfo(sampleinfo_raw)
        sacct_path = Path(sacct if sacct else f"{config_data['log']}.status")
        with sacct_path.open() as stream:
            sacct_jobs = sacct_api.parse_sacct(stream)
        run_data = self.parse(config_data, sampleinfo_data, sacct_jobs)
        new_run = self.build(run_data)
        if new_run:
            self.commit(new_run)
            return new_run

    @classmethod
    def parse(cls, config_data, sampleinfo_data, sacct_jobs):
        """Parse information about a run."""
        analysis_types = set(sample['type'] for sample in config_data['samples'])
        run_data = {
            'user': config_data['email'],
            'family': config_data['family'],
            'priority': config_data['priority'],
            'started_at': sampleinfo_data['date'],
            'version': sampleinfo_data['version'],
            'out_dir': config_data['out_dir'],
            'type': analysis_types.pop() if len(analysis_types) == 1 else 'wgs',
        }

        sacct_data, last_job_end = cls._parse_sacct(sacct_jobs)
        run_data.update(sacct_data)

        run_data['status'] = cls.get_status(sampleinfo_data['is_finished'],
                                            len(run_data['failed_jobs']))
        if run_data['status'] == 'completed':
            run_data['completed_at'] = last_job_end

        return run_data

    @staticmethod
    def _parse_sacct(sacct_jobs):
        """Parse out info from Sacct log."""
        failed_jobs = sacct_api.filter_jobs(sacct_jobs, failed=True)
        completed_jobs = [job for job in sacct_jobs if job['is_completed']]
        last_job_end = completed_jobs[-1]['end'] if len(completed_jobs) > 0 else None
        data = {
            'jobs': len(sacct_jobs),
            'completed_jobs': len(completed_jobs),
            'progress': len(completed_jobs) / len(sacct_jobs),
            'failed_jobs': [{
                'slurm_id': job['id'],
                'started_at': job['start'],
                'elapsed': job['elapsed'],
                'status': job['state'].lower(),
                'name': job['step'],
                'context': job['context'],
            } for job in failed_jobs]
        }
        return data, last_job_end

    @staticmethod
    def get_status(finished, failed_jobs):
        """Determine status of a run."""
        if finished:
            return 'completed'
        elif failed_jobs > 0:
            return 'failed'
        else:
            return 'running'

    def build(self, run_data):
        """Build a new Analysis object."""
        existing_run = self.store.find_analysis(family=run_data['family'],
                                                started_at=run_data['started_at'],
                                                status=run_data['status'],
                                                progress=run_data['progress'])
        if existing_run:
            return None

        run_data['user'] = self.store.user(run_data['user'])
        new_failed_jobs = [self.store.Job(**job) for job in run_data['failed_jobs']]
        del run_data['failed_jobs']
        new_run = self.store.Analysis(**run_data)
        new_run.failed_jobs = new_failed_jobs
        return new_run

    def commit(self, new_run):
        """Commit a new Analysis run to the store."""
        for temp_log in self.store.analyses(family=new_run.family, temp=True):
            temp_log.delete()
        self.store.add_commit(new_run)
