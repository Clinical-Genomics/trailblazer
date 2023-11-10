import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from trailblazer.apps.slurm.api import (
    cancel_slurm_job,
    get_current_analysis_status,
    get_slurm_squeue_output,
    get_squeue_result,
    reformat_squeue_result_job_step,
)
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.apps.tower.api import TowerAPI, get_tower_api
from trailblazer.constants import SlurmJobStatus, TrailblazerStatus, WorkflowManager
from trailblazer.exc import MissingAnalysis, TrailblazerError
from trailblazer.store.base import BaseHandler
from trailblazer.store.models import Analysis, Job, User

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler):
    """Class for updating items in the database."""

    def update_analysis_jobs(self, analysis: Analysis, jobs: List[dict]) -> None:
        """Update jobs in the analysis."""
        analysis.jobs = [Job(**job) for job in jobs]
        self.commit()

    def update_user_is_archived(self, user: User, archive: bool = True) -> None:
        """Update is archived for a user in the database."""
        user.is_archived = archive
        self.commit()

    def update_run_status(self, analysis_id: int, analysis_host: Optional[str] = None) -> None:
        """Query entries related to given analysis, and update the Trailblazer database."""
        analysis: Optional[Analysis] = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            LOG.warning(f"Analysis {analysis_id} not found!")
            return
        if analysis.workflow_manager == WorkflowManager.TOWER.value:
            self.update_tower_run_status(analysis_id=analysis_id)
        elif analysis.workflow_manager == WorkflowManager.SLURM.value:
            self.update_analysis_from_slurm_output(
                analysis_id=analysis_id, analysis_host=analysis_host
            )

    def update_ongoing_analyses(self, analysis_host: Optional[str] = None) -> None:
        """Iterate over all analysis with ongoing status and query SLURM for current progress."""
        ongoing_analyses: Optional[List[Analysis]] = self.get_analyses_with_statuses(
            statuses=list(TrailblazerStatus.ongoing_statuses())
        )
        for analysis in ongoing_analyses:
            try:
                self.update_run_status(analysis_id=analysis.id, analysis_host=analysis_host)
            except Exception as error:
                LOG.error(
                    f"Failed to update {analysis.family} - {analysis.id}: {type(error).__name__}"
                )

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
        self, analysis: Analysis, analysis_host: Optional[str] = False
    ) -> None:
        """Update analysis status based on current SLURM jobs status."""
        squeue_result: SqueueResult = get_squeue_result(
            squeue_response=get_slurm_squeue_output(
                analysis_host=analysis_host, slurm_job_id_file=Path(analysis.config_path)
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

    def update_tower_run_status(self, analysis_id: int) -> None:
        """Query tower for entries related to given analysis, and update the Trailblazer database."""
        analysis: Optional[Analysis] = self.get_analysis_with_id(analysis_id=analysis_id)
        tower_api: Optional[TowerAPI] = get_tower_api(
            config_file_path=analysis.config_path, case_id=analysis.family
        )

        try:
            self._update_analysis_from_tower_output(
                analysis=analysis, analysis_id=analysis_id, tower_api=tower_api
            )
        except Exception as error:
            LOG.error(f"Error logging case - {analysis.family} :  {type(error).__name__}")
            analysis.status = TrailblazerStatus.ERROR
            self.commit()

    def _update_analysis_from_tower_output(
        self, analysis: Analysis, analysis_id: int, tower_api: TowerAPI
    ):
        LOG.info(f"Status in Tower: {analysis.family} - {analysis_id} - {tower_api.workflow_id}")
        analysis.status = tower_api.status
        analysis.progress = tower_api.progress
        analysis.logged_at = datetime.now()
        self.delete_analysis_jobs(analysis=analysis)
        self.update_analysis_jobs(
            analysis=analysis, jobs=tower_api.get_jobs(analysis_id=analysis.id)
        )
        self.commit()
        LOG.debug(f"Updated status {analysis.family} - {analysis.id}: {analysis.status} ")

    def update_analysis_from_slurm_output(
        self, analysis_id: int, analysis_host: Optional[str] = False
    ) -> None:
        """Query SLURM for entries related to given analysis, and update the analysis in the database."""
        analysis: Optional[Analysis] = self.get_analysis_with_id(analysis_id=analysis_id)
        try:
            self._update_analysis_from_slurm_squeue_output(
                analysis=analysis, analysis_host=analysis_host
            )
        except Exception as exception:
            LOG.error(
                f"Error updating analysis for: case - {analysis.family} : {exception.__class__.__name__}"
            )
            analysis.status = TrailblazerStatus.ERROR
            self.commit()

    def update_case_analyses_as_deleted(self, case_id: str) -> Optional[List[Analysis]]:
        """Mark analyses connected to a case as deleted."""
        analyses: Optional[List[Analysis]] = self.get_analyses_for_case(case_id=case_id)
        if analyses:
            for analysis in analyses:
                analysis.is_deleted = True
            self.commit()
        return analyses

    def cancel_ongoing_analysis(
        self, analysis_id: int, analysis_host: Optional[str] = None, email: Optional[str] = None
    ) -> None:
        """Cancel all ongoing slurm jobs associated with the analysis, and set analysis status to 'cancelled'.
        Raises:
            MissingAnalysis when no analysis.
            TrailblazerError for no ongoing analysis for analysis id.
        """
        analysis: Optional[Analysis] = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            raise MissingAnalysis(f"Analysis {analysis_id} does not exist")
        if analysis.status not in TrailblazerStatus.ongoing_statuses():
            raise TrailblazerError(f"Analysis {analysis_id} is not running")
        if analysis.workflow_manager == WorkflowManager.TOWER.value:
            self.cancel_tower_analysis(analysis=analysis)
        else:
            self.cancel_slurm_analysis(analysis=analysis, analysis_host=analysis_host)
        LOG.info(f"Case {analysis.family} - Analysis {analysis.id}: cancelled successfully!")
        self.update_run_status(analysis_id=analysis_id, analysis_host=analysis_host)
        analysis.status = TrailblazerStatus.CANCELLED
        analysis.comment = (
            f"Analysis cancelled manually by user:"
            f" {(self.get_user(email=email).name if self.get_user(email=email) else (email or 'Unknown'))}!"
        )
        self.commit()

    def cancel_slurm_analysis(
        self, analysis: Analysis, analysis_host: Optional[str] = None
    ) -> None:
        """Cancel SLURM analysis by cancelling all associated SLURM jobs."""
        for job in analysis.jobs:
            if job.status in SlurmJobStatus.ongoing_statuses():
                LOG.info(f"Cancelling job {job.slurm_id} - {job.name}")
                cancel_slurm_job(analysis_host=analysis_host, slurm_id=job.slurm_id)

    def cancel_tower_analysis(self, analysis: Analysis) -> None:
        """Cancel a NF-Tower analysis. Associated jobs are cancelled by Tower."""
        LOG.info(f"Cancelling Tower workflow for {analysis.family}")
        tower_api: TowerAPI = get_tower_api(
            config_file_path=analysis.config_path, case_id=analysis.family
        )
        tower_api.cancel()

    def update_analysis_status(self, case_id: str, status: str):
        """Setting analysis status."""
        status: str = status.lower()
        if status not in set(TrailblazerStatus.statuses()):
            raise ValueError(f"Invalid status. Allowed values are: {TrailblazerStatus.statuses()}")
        analysis: Optional[Analysis] = self.get_latest_analysis_for_case(case_id=case_id)
        analysis.status = status
        self.commit()
        LOG.info(f"{analysis.family} - Status set to {status.upper()}")

    def update_analysis_status_to_completed(self, analysis_id: int) -> None:
        """Set an analysis status to 'completed'."""
        analysis: Optional[Analysis] = self.get_analysis_with_id(analysis_id=analysis_id)
        self.update_analysis_status(case_id=analysis.family, status=TrailblazerStatus.COMPLETED)

    def update_analysis_uploaded_at(self, case_id: str, uploaded_at: datetime) -> None:
        """Set analysis uploaded at for an analysis."""
        analysis: Optional[Analysis] = self.get_latest_analysis_for_case(case_id=case_id)
        analysis.uploaded_at = uploaded_at
        self.commit()

    def update_analysis_comment(self, case_id: str, comment: str) -> None:
        analysis: Optional[Analysis] = self.get_latest_analysis_for_case(case_id=case_id)
        analysis.comment: str = (
            " ".join([analysis.comment, comment]) if analysis.comment else comment
        )
        self.commit()
        LOG.info(f"Adding comment {comment} to analysis {analysis.family}")
