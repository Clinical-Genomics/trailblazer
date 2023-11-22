import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

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
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis, Job, User

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler):
    """Class for updating items in the database."""

    def update_analysis_jobs(self, analysis: Analysis, jobs: list[dict]) -> None:
        """Update jobs in the analysis."""
        analysis.jobs = [Job(**job) for job in jobs]
        session: Session = get_session()
        session.commit()

    def update_user_is_archived(self, user: User, archive: bool = True) -> None:
        """Update is archived for a user in the database."""
        user.is_archived = archive
        session: Session = get_session()
        session.commit()

    def update_run_status(self, analysis_id: int, analysis_host: str | None = None) -> None:
        """Query entries related to given analysis, and update the Trailblazer database."""
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            LOG.warning(f"Analysis {analysis_id} not found!")
            return
        if analysis.workflow_manager == WorkflowManager.TOWER:
            self.update_tower_run_status(analysis_id=analysis_id)
        elif analysis.workflow_manager == WorkflowManager.SLURM:
            self.update_analysis_from_slurm_output(
                analysis_id=analysis_id, analysis_host=analysis_host
            )

    def update_ongoing_analyses(self, analysis_host: str | None = None) -> None:
        """Iterate over all analysis with ongoing status and query SLURM for current progress."""
        ongoing_analyses: list[Analysis] | None = self.get_analyses_with_statuses(
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
        session: Session = get_session()
        session.commit()

    def _update_analysis_from_slurm_squeue_output(
        self, analysis: Analysis, analysis_host: str | None = False
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
        session: Session = get_session()
        session.commit()

    def update_tower_run_status(self, analysis_id: int) -> None:
        """Query tower for entries related to given analysis, and update the Trailblazer database."""
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id=analysis_id)
        tower_api: TowerAPI | None = get_tower_api(
            config_file_path=analysis.config_path, case_id=analysis.family
        )

        try:
            self._update_analysis_from_tower_output(
                analysis=analysis, analysis_id=analysis_id, tower_api=tower_api
            )
        except Exception as error:
            LOG.error(f"Error logging case - {analysis.family} :  {type(error).__name__}")
            analysis.status = TrailblazerStatus.ERROR
            session: Session = get_session()
            session.commit()

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
        session: Session = get_session()
        session.commit()
        LOG.debug(f"Updated status {analysis.family} - {analysis.id}: {analysis.status} ")

    def update_analysis_from_slurm_output(
        self, analysis_id: int, analysis_host: str | None = False
    ) -> None:
        """Query SLURM for entries related to given analysis, and update the analysis in the database."""
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id=analysis_id)
        try:
            self._update_analysis_from_slurm_squeue_output(
                analysis=analysis, analysis_host=analysis_host
            )
        except Exception as exception:
            LOG.error(
                f"Error updating analysis for: case - {analysis.family} : {exception.__class__.__name__}"
            )
            analysis.status = TrailblazerStatus.ERROR
            session: Session = get_session()
            session.commit()

    def update_case_analyses_as_deleted(self, case_id: str) -> list[Analysis] | None:
        """Mark analyses connected to a case as deleted."""
        analyses: list[Analysis] | None = self.get_analyses_for_case(case_id=case_id)
        if analyses:
            for analysis in analyses:
                analysis.is_deleted = True
            session: Session = get_session()
            session.commit()
        return analyses

    def cancel_ongoing_analysis(
        self, analysis_id: int, analysis_host: str | None = None, email: str | None = None
    ) -> None:
        """Cancel all ongoing slurm jobs associated with the analysis, and set analysis status to 'cancelled'.
        Raises:
            MissingAnalysis when no analysis.
            TrailblazerError for no ongoing analysis for analysis id.
        """
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            raise MissingAnalysis(f"Analysis {analysis_id} does not exist")
        if analysis.status not in TrailblazerStatus.ongoing_statuses():
            raise TrailblazerError(f"Analysis {analysis_id} is not running")
        if analysis.workflow_manager == WorkflowManager.TOWER:
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
        session: Session = get_session()
        session.commit()

    def cancel_slurm_analysis(self, analysis: Analysis, analysis_host: str | None = None) -> None:
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
        analysis: Analysis | None = self.get_latest_analysis_for_case(case_id=case_id)
        analysis.status = status
        session: Session = get_session()
        session.commit()
        LOG.info(f"{analysis.family} - Status set to {status.upper()}")

    def update_analysis_status_to_completed(self, analysis_id: int) -> None:
        """Set an analysis status to 'completed'."""
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id=analysis_id)
        self.update_analysis_status(case_id=analysis.family, status=TrailblazerStatus.COMPLETED)

    def update_analysis_uploaded_at(self, case_id: str, uploaded_at: datetime) -> None:
        """Set analysis uploaded at for an analysis."""
        analysis: Analysis | None = self.get_latest_analysis_for_case(case_id=case_id)
        analysis.uploaded_at = uploaded_at
        session: Session = get_session()
        session.commit()

    def update_analysis_comment(self, case_id: str, comment: str) -> None:
        analysis: Analysis | None = self.get_latest_analysis_for_case(case_id=case_id)
        analysis.comment: str = (
            " ".join([analysis.comment, comment]) if analysis.comment else comment
        )
        session: Session = get_session()
        session.commit()
        LOG.info(f"Adding comment {comment} to analysis {analysis.family}")

    def update_analysis(
        self,
        analysis_id: int,
        status: str | None = None,
        comment: str | None = None,
        is_visible: bool | None = None,
    ) -> Analysis:
        """Update an analysis."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id)

        if comment:
            LOG.info(f"Adding comment {comment} to analysis {analysis.family}")
            analysis.comment = comment

        if is_visible:
            LOG.info(f"Setting visibility to {is_visible} for analysis {analysis.family}")
            analysis.is_visible = bool(is_visible)

        if status:
            self.update_analysis_status(case_id=analysis.family, status=status)

        session: Session = get_session()
        session.commit()

        return analysis
