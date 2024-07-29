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
from trailblazer.services.tower.tower_api_service import TowerAPIService, get_tower_api
from trailblazer.constants import SlurmJobStatus, TrailblazerStatus, WorkflowManager
from trailblazer.dto.update_analyses import UpdateAnalyses
from trailblazer.exc import MissingAnalysis, TrailblazerError
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.store.base import BaseHandler
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis, Delivery, Job, User

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler):
    """Class for updating items in the database."""

    def update_jobs(self, jobs: list[dict]) -> None:
        """Update jobs in the analysis."""
        session: Session = get_session()
        for job in jobs:
            updated_job = Job(**job)
            session.add(updated_job)
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
            self.update_tower_run_status(analysis_id)
        elif analysis.workflow_manager == WorkflowManager.SLURM:
            self.update_analysis_from_slurm_output(
                analysis_id=analysis_id, analysis_host=analysis_host
            )

    def update_ongoing_analyses(self, analysis_host: str | None = None) -> None:
        """Iterate over all analysis with ongoing status and query SLURM for current progress."""
        ongoing_analyses: list[Analysis] = self.get_ongoing_analyses()
        for analysis in ongoing_analyses:
            try:
                self.update_run_status(analysis_id=analysis.id, analysis_host=analysis_host)
            except Exception as error:
                LOG.error(f"Failed to update {analysis.case_id} - {analysis.id}: {error}")

    def get_ongoing_analyses(self) -> list[Analysis]:
        """Return all analyses with ongoing status."""
        ongoing_statuses: list[str] = list(TrailblazerStatus.ongoing_statuses())
        return self.get_analyses_with_statuses(ongoing_statuses)

    def update_analysis_jobs_from_slurm_jobs(
        self, analysis: Analysis, squeue_result: SqueueResult
    ) -> None:
        """Update analysis jobs from supplied squeue results."""
        if len(squeue_result.jobs) == 0:
            return
        self.delete_analysis_jobs(analysis)

        session: Session = get_session()
        for job in squeue_result.jobs:
            job.step = reformat_squeue_result_job_step(
                workflow=analysis.workflow, job_step=job.step
            )
            new_job = Job(
                analysis_id=analysis.id,
                slurm_id=job.id,
                name=job.step,
                status=job.status,
                started_at=job.started_at,
                elapsed=job.time_elapsed,
            )
            session.add(new_job)
        session.commit()

    def _update_analysis_from_slurm_squeue_output(
        self, analysis: Analysis, analysis_host: str | None = False
    ) -> None:
        """Update analysis status based on current SLURM jobs status."""
        slurm_job_id_file = Path(analysis.config_path)
        queue_output = get_slurm_squeue_output(
            analysis_host=analysis_host, slurm_job_id_file=slurm_job_id_file
        )
        squeue_result: SqueueResult = get_squeue_result(queue_output)
        self.update_analysis_jobs_from_slurm_jobs(analysis=analysis, squeue_result=squeue_result)
        LOG.debug(f"Status in SLURM: {analysis.case_id} - {analysis.id}")
        LOG.debug(squeue_result.jobs)
        analysis.progress = squeue_result.jobs_status_distribution.get(
            SlurmJobStatus.COMPLETED, 0.0
        )
        analysis.status = get_current_analysis_status(squeue_result.jobs_status_distribution)
        LOG.info(f"Updated status {analysis.case_id} - {analysis.id}: {analysis.status} ")
        analysis.logged_at = datetime.now()
        session: Session = get_session()
        session.commit()

    def update_tower_run_status(self, analysis_id: int) -> None:
        """Query tower for entries related to given analysis, and update the Trailblazer database."""
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)
        tower_api: TowerAPIService | None = get_tower_api(
            config_file_path=analysis.config_path, case_id=analysis.case_id
        )

        try:
            self._update_analysis_from_tower_output(
                analysis=analysis, analysis_id=analysis_id, tower_api=tower_api
            )
        except Exception as error:
            LOG.error(f"Error logging case - {analysis.case_id} :  {type(error).__name__}")
            analysis.status = TrailblazerStatus.ERROR
            session: Session = get_session()
            session.commit()

    def _update_analysis_from_tower_output(
        self, analysis: Analysis, analysis_id: int, tower_api: TowerAPIService
    ):
        LOG.info(f"Status in Tower: {analysis.case_id} - {analysis_id} - {tower_api.workflow_id}")
        analysis.status = tower_api.status
        analysis.progress = tower_api.progress
        analysis.logged_at = datetime.now()
        self.delete_analysis_jobs(analysis)
        jobs: list[dict] = tower_api.get_jobs(analysis.id)
        self.update_jobs(jobs)
        session: Session = get_session()
        session.commit()
        LOG.debug(f"Updated status {analysis.case_id} - {analysis.id}: {analysis.status} ")

    def update_analysis_from_slurm_output(
        self, analysis_id: int, analysis_host: str | None = False
    ) -> None:
        """Query SLURM for entries related to given analysis, and update the analysis in the database."""
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)
        try:
            self._update_analysis_from_slurm_squeue_output(
                analysis=analysis, analysis_host=analysis_host
            )
        except Exception as exception:
            LOG.error(f"Error updating analysis for: case - {analysis.case_id} : {exception}")
            analysis.status = TrailblazerStatus.ERROR
            session: Session = get_session()
            session.commit()

    def cancel_ongoing_analysis(
        self, analysis_id: int, analysis_host: str | None = None, email: str | None = None
    ) -> None:
        """Cancel all ongoing slurm jobs associated with the analysis, and set analysis status to 'cancelled'.
        Raises:
            MissingAnalysis when no analysis.
            TrailblazerError for no ongoing analysis for analysis id.
        """
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)
        if not analysis:
            raise MissingAnalysis(f"Analysis {analysis_id} does not exist")
        if analysis.status not in TrailblazerStatus.ongoing_statuses():
            raise TrailblazerError(f"Analysis {analysis_id} is not running")
        if analysis.workflow_manager == WorkflowManager.TOWER:
            self.cancel_tower_analysis(analysis)
        else:
            self.cancel_slurm_analysis(analysis=analysis, analysis_host=analysis_host)
        LOG.info(f"Case {analysis.case_id} - Analysis {analysis.id}: cancelled successfully!")
        self.update_run_status(analysis_id=analysis_id, analysis_host=analysis_host)
        analysis.status = TrailblazerStatus.CANCELLED
        new_comment: str = (
            f"Analysis cancelled manually by user:"
            f" {(self.get_user(email=email).name if self.get_user(email=email) else (email or 'Unknown'))}!"
        )
        self.update_analysis_comment(analysis=analysis, comment=new_comment)
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
        LOG.info(f"Cancelling Tower workflow for {analysis.case_id}")
        tower_api: TowerAPIService = get_tower_api(
            config_file_path=analysis.config_path, case_id=analysis.case_id
        )
        tower_api.cancel()

    def update_analysis_status_by_case_id(self, case_id: str, status: str):
        """Setting analysis status."""
        status: str = status.lower()
        if status not in set(TrailblazerStatus.statuses()):
            raise ValueError(f"Invalid status. Allowed values are: {TrailblazerStatus.statuses()}")
        analysis: Analysis | None = self.get_latest_analysis_for_case(case_id)
        analysis.status = status
        session: Session = get_session()
        session.commit()
        LOG.info(f"{analysis.case_id} - Status set to {status.upper()}")

    def update_analysis_status_to_completed(self, analysis_id: int) -> None:
        """Set an analysis status to 'completed'."""
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)
        self.update_analysis_status_by_case_id(
            case_id=analysis.case_id, status=TrailblazerStatus.COMPLETED
        )

    def update_analysis_uploaded_at(self, case_id: str, uploaded_at: datetime) -> None:
        """Set analysis uploaded at for an analysis."""
        analysis: Analysis | None = self.get_latest_analysis_for_case(case_id)
        analysis.uploaded_at = uploaded_at
        session: Session = get_session()
        session.commit()

    def update_latest_analysis_comment(self, case_id: str, comment: str) -> None:
        analysis: Analysis | None = self.get_latest_analysis_for_case(case_id)
        self.update_analysis_comment(analysis=analysis, comment=comment)

    @staticmethod
    def update_analysis_comment(analysis: Analysis, comment: str):
        analysis.comment: str = (
            " ".join([analysis.comment, comment]) if analysis.comment else comment
        )
        session: Session = get_session()
        session.commit()
        LOG.info(f"Adding comment {comment} to analysis {analysis.case_id}")

    @staticmethod
    def update_analysis_delivery(
        analysis: Analysis, is_delivered: bool, user: User | None = None
    ) -> None:
        session: Session = get_session()
        if is_delivered and not analysis.delivery:
            delivery = Delivery(
                analysis_id=analysis.id,
                delivered_by=user.id,
                delivered_date=datetime.today(),
            )
            session.add(delivery)
            session.commit()
            analysis.delivery = delivery
        elif not is_delivered:
            if delivery := analysis.delivery:
                session.delete(delivery)

    def update_analysis(
        self,
        analysis_id: int,
        comment: str | None = None,
        is_delivered: bool | None = None,
        is_visible: bool | None = None,
        status: str | None = None,
        user: User | None = None,
    ) -> Analysis:
        """Update an analysis."""
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)

        if not analysis:
            raise MissingAnalysis(f"Analysis {analysis_id} does not exist")

        if comment is not None:
            LOG.info(f"Adding comment {comment} to analysis {analysis.id}")
            analysis.comment = comment

        if is_delivered is not None:
            LOG.info(f"Setting analysis delivered status to {is_delivered}")
            self.update_analysis_delivery(analysis=analysis, is_delivered=is_delivered, user=user)

        if is_visible is not None:
            LOG.info(f"Setting visibility to {is_visible} for analysis {analysis.id}")
            analysis.is_visible = bool(is_visible)

        if status is not None:
            LOG.info(f"Setting status to {status} for analysis {analysis.id}")
            analysis.status = status

        session: Session = get_session()
        session.commit()

        return analysis

    def update_analyses(self, data: UpdateAnalyses, user: User | None = None) -> list[Analysis]:
        updated_analyses: list[Analysis] = []
        for analysis_update in data.analyses:
            analysis: Analysis = self.update_analysis(
                analysis_id=analysis_update.id,
                is_delivered=analysis_update.is_delivered,
                comment=analysis_update.comment,
                is_visible=analysis_update.is_visible,
                status=analysis_update.status,
                user=user,
            )
            updated_analyses.append(analysis)
        return updated_analyses

    def update_job(self, job_id: int, job_info: SlurmJobInfo) -> Job:
        job: Job | None = self.get_job_by_id(job_id)
        job.name = job_info.name
        job.status = job_info.status
        job.elapsed = job_info.elapsed
        job.started_at = job_info.started_at
        session: Session = get_session()
        session.commit()

    def update_user_token(self, refresh_token: str, user_id: int) -> None:
        user: User | None = self.get_user_by_id(user_id)
        user.refresh_token = refresh_token
        session: Session = get_session()
        session.commit()

    def update_analysis_status(self, analysis_id: int, status: TrailblazerStatus) -> None:
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)
        analysis.status = status
        session: Session = get_session()
        session.commit()
        LOG.info(f"Updated status {analysis.case_id} - {analysis.id}: {analysis.status} ")

    def update_analysis_progress(self, analysis_id: int, progress: float) -> None:
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)
        analysis.progress = progress
        session: Session = get_session()
        session.commit()

    def update_analysis_upload_date(self, analysis_id: int, uploaded_at: datetime) -> None:
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)
        analysis.uploaded_at = uploaded_at
        session: Session = get_session()
        session.commit()
