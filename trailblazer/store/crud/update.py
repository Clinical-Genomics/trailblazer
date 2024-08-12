import logging
from datetime import datetime
from sqlalchemy.orm import Session

from trailblazer.constants import TrailblazerStatus
from trailblazer.dto.update_analyses import UpdateAnalyses
from trailblazer.exc import MissingAnalysis
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

    def get_ongoing_analyses(self) -> list[Analysis]:
        """Return all analyses with ongoing status."""
        ongoing_statuses: list[str] = list(TrailblazerStatus.ongoing_statuses())
        return self.get_analyses_with_statuses(ongoing_statuses)

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
        self.update_analysis_comment(analysis_id=analysis.id, comment=comment)

    def update_analysis_comment(self, analysis_id: int, comment: str):
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id)
        analysis.comment = " ".join([analysis.comment, comment]) if analysis.comment else comment
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
