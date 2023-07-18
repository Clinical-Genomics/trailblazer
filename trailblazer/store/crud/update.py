from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import User, Analysis
from trailblazer.store.utils import formatters


class UpdateHandler(BaseHandler_2):
    """Class for updating items in the database."""

    def add_user(self, name: str, email: str) -> User:
        """Add a new user to the database."""
        new_user: User = User(email=email, name=name)
        self.add_commit(new_user)
        return new_user

    def update_user_is_archived(self, user: User, archive: bool = True) -> None:
        """Update is archived fpr a user in the database."""
        user.is_archived = archive
        self.commit()

    def update_slurm_jobs(self, analysis: Analysis, squeue_result: SqueueResult) -> None:
        """Update analysis failed jobs from supplied squeue results."""
        if len(squeue_result.jobs) == 0:
            return
        formatter_func = formatters.formatter_map.get(
            analysis.data_analysis, formatters.transform_undefined
        )
        for job in squeue_result.jobs:
            job.step = formatter_func(job.step)

        for job_obj in analysis.failed_jobs:
            job_obj.delete()
        self.commit()
        analysis.failed_jobs = [
            self.Job(
                analysis_id=analysis.id,
                slurm_id=job.id,
                name=job.step,
                status=job.status,
                started_at=job.started,
                elapsed=job.time_elapsed,
            )
            for job in squeue_result.jobs
        ]
        self.commit()
