from datetime import datetime

from sqlalchemy.orm import Session

from trailblazer.constants import SlurmJobStatus, TrailblazerStatus
from trailblazer.dto.create_analysis_request import CreateAnalysisRequest
from trailblazer.dto.create_job_request import CreateJobRequest
from trailblazer.store.base import BaseHandler
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis, Job, User


class CreateHandler(BaseHandler):
    """Class for creating items in the database."""

    def add_pending_analysis(self, analysis_data: CreateAnalysisRequest) -> Analysis:
        session: Session = get_session()

        new_analysis = Analysis(
            config_path=analysis_data.config_path,
            workflow=analysis_data.workflow,
            case_id=analysis_data.case_id,
            out_dir=analysis_data.out_dir,
            order_id=analysis_data.order_id,
            priority=analysis_data.priority,
            started_at=datetime.now(),
            status=TrailblazerStatus.PENDING,
            ticket_id=analysis_data.ticket,
            type=analysis_data.type,
            workflow_manager=analysis_data.workflow_manager,
        )

        if analysis_data.email:
            user: User = self.get_user(analysis_data.email)
            new_analysis.user = user

        session.add(new_analysis)
        session.commit()
        return new_analysis

    def add_user(self, name: str, email: str, abbreviation: str) -> User:
        """Add a new user to the database."""
        session: Session = get_session()
        new_user = User(email=email, name=name, abbreviation=abbreviation)
        session.add(new_user)
        session.commit()
        return new_user

    def add_job(self, analysis_id: int, job_request: CreateJobRequest) -> Job:
        """Add a new job to the database."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id)
        job = Job(
            status=SlurmJobStatus.PENDING,
            slurm_id=job_request.slurm_id,
            job_type=job_request.job_type,
        )
        analysis.jobs.append(job)
        session: Session = get_session()
        session.commit()
        return job

    def replace_jobs(self, analysis_id: int, jobs: list[Job]):
        analysis: Analysis = self.get_analysis_with_id(analysis_id)
        self.delete_analysis_jobs(analysis)
        for job in jobs:
            analysis.jobs.append(job)
        session: Session = get_session()
        session.commit()
