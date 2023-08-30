import logging
from datetime import datetime
from pathlib import Path
from typing import List

from trailblazer.apps.slurm.api import (
    get_current_analysis_status,
    get_slurm_squeue_output,
    get_squeue_result,
    reformat_squeue_result_job_step,
)
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.constants import SlurmJobStatus
from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import Analysis, Job, User

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler_2):
    """Class for updating items in the database."""

    def update_analysis_jobs(self, analysis: Analysis, jobs: List[dict]) -> None:
        """Update jobs in the analysis."""
        analysis.jobs = [Job(**job) for job in jobs]
        self.commit()

    def update_user_is_archived(self, user: User, archive: bool = True) -> None:
        """Update is archived for a user in the database."""
        user.is_archived = archive
        self.commit()

    def update_analysis_jobs_from_slurm_jobs(
        self, analysis: Analysis, squeue_result: SqueueResult
    ) -> None:
        """Update analysis jobs from supplied squeue results."""
        if len(squeue_result.jobs) == 0:
            return
        for job in squeue_result.jobs:
            job.step = reformat_squeue_result_job_step(
                data_analysis=analysis.data_analysis, job_step=job.step
            )

        self.delete_analysis_jobs(analysis=analysis)
        analysis.jobs = [
            Job(
                analysis_id=analysis.id,
                slurm_id=job.id,
                name=job.step,
                status=job.status,
                started_at=job.started_at,
                elapsed=job.time_elapsed,
            )
            for job in squeue_result.jobs
        ]
        self.commit()

    def _update_analysis_from_slurm_squeue_output(
        self, analysis: Analysis, use_ssh: bool = False
    ) -> None:
        """Update analysis status based on current SLURM jobs status."""
        squeue_result: SqueueResult = get_squeue_result(
            squeue_response=get_slurm_squeue_output(
                slurm_job_id_file=Path(analysis.config_path, use_ssh=use_ssh)
            )
        )
        self.update_analysis_jobs_from_slurm_jobs(analysis=analysis, squeue_result=squeue_result)
        LOG.debug(f"Status in SLURM: {analysis.family} - {analysis.id}")
        LOG.debug(squeue_result.jobs)
        analysis.progress = squeue_result.jobs_status_distribution.get(
            SlurmJobStatus.COMPLETED, 0.0
        )
        analysis.status = get_current_analysis_status(
            jobs_status_distribution=squeue_result.jobs_status_distribution
        )
        LOG.info(f"Updated status {analysis.family} - {analysis.id}: {analysis.status} ")
        analysis.logged_at = datetime.now()
        self.commit()
