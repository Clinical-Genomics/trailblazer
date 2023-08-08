from trailblazer.apps.slurm.api import reformat_squeue_result_job_step
from trailblazer.apps.slurm.models import SqueueResult
from typing import List

from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import User, Analysis, Job


class UpdateHandler(BaseHandler_2):
    """Class for updating items in the database."""

    def update_analysis_jobs(self, analysis: Analysis, jobs: List[dict]) -> None:
        """Update jobs in the analysis."""
        # failed_jobs is misnamed and actually contains all jobs irrespective of status
        analysis.failed_jobs = [Job(**job) for job in jobs]
        self.commit()

    def update_user_is_archived(self, user: User, archive: bool = True) -> None:
        """Update is archived for a user in the database."""
        user.is_archived = archive
        self.commit()

    def update_analysis_jobs_from_slurm_jobs(
        self, analysis: Analysis, squeue_result: SqueueResult
    ) -> None:
        """Update analysis failed jobs from supplied squeue results."""
        if len(squeue_result.jobs) == 0:
            return
        for job in squeue_result.jobs:
            job.step = reformat_squeue_result_job_step(
                data_analysis=analysis.data_analysis, job_step=job.step
            )

        self.delete_analysis_jobs(analysis=analysis)
        analysis.failed_jobs = [
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
