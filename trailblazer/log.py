# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from typing import List

import ruamel.yaml

from trailblazer.mip import sacct as sacct_api, files as files_api, miplog
from trailblazer.store import models, Store
from trailblazer.exc import MissingFileError

log = logging.getLogger(__name__)


class LogAnalysis(object):

    def __init__(self, store: Store):
        self.store = store

    def __call__(self, config_stream: List[str], sampleinfo: str=None, sacct: str=None):
        """Add a new analysis log."""
        config_raw = ruamel.yaml.safe_load(config_stream)
        config_data = files_api.parse_config(config_raw)
        sampleinfo_path = Path(sampleinfo or config_data['sampleinfo_path'])
        if not sampleinfo_path.exists():
            raise MissingFileError(sampleinfo_path)
        with sampleinfo_path.open() as stream:
            sampleinfo_raw = ruamel.yaml.safe_load(stream)
        sampleinfo_data = files_api.parse_sampleinfo(sampleinfo_raw)
        sacct_path = Path(sacct if sacct else f"{config_data['log_path']}.status")
        if not sacct_path.exists():
            raise MissingFileError(sacct_path)
        with sacct_path.open() as stream:
            sacct_jobs = sacct_api.parse_sacct(stream)
        with Path(config_data['log_path']).open() as stream:
            jobs = len(miplog.job_ids(stream))
        run_data = self.parse(config_data, sampleinfo_data, sacct_jobs, jobs=jobs)
        self._delete_temp_logs(run_data['family'])
        new_run = self.build(run_data)
        if new_run:
            self.store.add_commit(new_run)
            return new_run

    def _delete_temp_logs(self, family_name: str):
        """Delete temporary logs for the current family."""
        for temp_log in self.store.analyses(family=family_name, temp=True):
            log.debug(f"delete temporary log: {temp_log.id} - {temp_log.status}")
            temp_log.delete()

    @classmethod
    def parse(cls, config_data: dict, sampleinfo_data: dict, sacct_jobs: List[dict],
              jobs: int) -> dict:
        """Parse information about a run."""
        analysis_types = [sample['type'] for sample in config_data['samples']]
        run_data = {
            'user': config_data['email'],
            'family': config_data['family'],
            'priority': config_data['priority'],
            'started_at': sampleinfo_data['date'],
            'version': sampleinfo_data['version'],
            'out_dir': config_data['out_dir'],
            'config_path': config_data['config_path'],
            'type': cls._get_analysis_type(analysis_types),
        }

        sacct_data, last_job_end = cls._parse_sacct(sacct_jobs, jobs_count=jobs)
        run_data.update(sacct_data)

        run_data['status'] = cls.get_status(sampleinfo_data['is_finished'],
                                            len(run_data['failed_jobs']))
        if run_data['status'] == 'completed':
            run_data['completed_at'] = last_job_end

        return run_data

    @staticmethod
    def _parse_sacct(sacct_jobs: List[dict], jobs_count: int=None):
        """Parse out info from Sacct log."""
        failed_jobs = sacct_api.filter_jobs(sacct_jobs, failed=True)
        completed_jobs = [job for job in sacct_jobs if job['is_completed']]
        last_job_end = completed_jobs[-1]['end'] if len(completed_jobs) > 0 else None
        data = {
            'jobs': jobs_count,
            'completed_jobs': len(completed_jobs),
            'progress': (len(completed_jobs) / jobs_count) if jobs_count else None,
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
    def get_status(finished: str, failed_jobs: int) -> str:
        """Determine status of a run."""
        if finished:
            return 'completed'
        elif failed_jobs > 0:
            return 'failed'
        else:
            return 'running'

    @staticmethod
    def _get_analysis_type(analysis_types: List[str]) -> str:
        """Determine the overall analysis type."""
        types_set = set(analysis_types)
        return types_set.pop() if len(types_set) == 1 else 'wgs'

    def build(self, run_data: dict) -> models.Analysis:
        """Build a new Analysis object."""
        existing_run = self.store.find_analysis(family=run_data['family'],
                                                started_at=run_data['started_at'],
                                                status=run_data['status'])
        if existing_run:
            return None

        run_data['user'] = self.store.user(run_data['user'])
        new_failed_jobs = [self.store.Job(**job) for job in run_data['failed_jobs']]
        del run_data['failed_jobs']
        new_run = self.store.Analysis(**run_data)
        new_run.failed_jobs = new_failed_jobs
        return new_run
