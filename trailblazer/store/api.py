"""Store backend in Trailblazer."""
import datetime as dt
import logging
import subprocess
from pathlib import Path
from typing import Any, Optional

import alchy
import sqlalchemy as sqa
from alchy import Query

from trailblazer.apps.slurm.api import get_current_analysis_status, get_squeue_result
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.apps.tower.api import TowerAPI
from trailblazer.constants import FileFormat, SlurmJobStatus, TrailblazerStatus, WorkflowManager
from trailblazer.exc import TowerRequirementsError, TrailblazerError
from trailblazer.io.controller import ReadFile
from trailblazer.store.core import CoreHandler
from trailblazer.store.models import Analysis, Model


LOG = logging.getLogger(__name__)


class BaseHandler(CoreHandler):
    Analysis = Analysis

    def setup(self):
        self.create_all()

    def get_analysis(self, case_id: str, started_at: dt.datetime, status: str) -> Analysis:
        """
        used in LOG
        Find a single analysis."""
        query = self.Analysis.query.filter_by(family=case_id, started_at=started_at, status=status)
        return query.first()

    def analyses(
        self,
        case_id: str = None,
        query: str = None,
        status: str = None,
        deleted: bool = None,
        temp: bool = False,
        before: dt.datetime = None,
        is_visible: bool = None,
        family: str = None,
        data_analysis: str = None,
        comment: str = None,
    ) -> Query:
        """
        used by REST +> CG
        Fetch analyses from the database."""
        if not case_id:
            case_id = family

        analysis_query = self.Analysis.query
        if case_id:
            analysis_query = analysis_query.filter_by(family=case_id)
        if query:  # to be deprecated
            analysis_query = analysis_query.filter(
                sqa.or_(
                    self.Analysis.family.ilike(f"%{query}%"),
                    self.Analysis.status.ilike(f"%{query}%"),
                    self.Analysis.data_analysis.ilike(f"%{query}%"),
                    self.Analysis.comment.ilike(f"%{query}%"),
                )
            )
        if status:
            analysis_query = analysis_query.filter_by(status=status)
        if isinstance(deleted, bool):
            analysis_query = analysis_query.filter_by(is_deleted=deleted)
        if temp:
            analysis_query = analysis_query.filter(
                self.Analysis.status.in_(TrailblazerStatus.ongoing_statuses())
            )
        if before:
            analysis_query = analysis_query.filter(self.Analysis.started_at < before)
        if is_visible is not None:
            analysis_query = analysis_query.filter_by(is_visible=is_visible)
        if data_analysis:
            analysis_query = analysis_query.filter(
                Analysis.data_analysis.ilike(f"%{data_analysis}%")
            )
        if comment:
            analysis_query = analysis_query.filter(Analysis.comment.ilike(f"%{comment}%"))

        return analysis_query.order_by(self.Analysis.started_at.desc())

    def get_latest_analysis(self, case_id: str) -> Optional[Analysis]:
        return self.analyses(case_id=case_id).first()

    def get_latest_analysis_status(self, case_id: str) -> Optional[str]:
        """Get the latest analysis status for a case_id"""
        latest_analysis = self.get_latest_analysis(case_id=case_id)
        if latest_analysis:
            return latest_analysis.status

    def is_latest_analysis_ongoing(self, case_id: str) -> bool:
        """Check if the latest analysis is ongoing for a case_id"""
        latest_analysis_status = self.get_latest_analysis_status(case_id=case_id)
        return latest_analysis_status in TrailblazerStatus.ongoing_statuses()

    def is_latest_analysis_failed(self, case_id: str) -> bool:
        """Check if the latest analysis is failed for a case_id"""
        latest_analysis_status = self.get_latest_analysis_status(case_id=case_id)
        return latest_analysis_status == TrailblazerStatus.FAILED

    def is_latest_analysis_completed(self, case_id: str) -> bool:
        """Check if the latest analysis is completed for a case_id"""
        latest_analysis = self.analyses(case_id=case_id).first()
        return bool(latest_analysis and latest_analysis.status == TrailblazerStatus.COMPLETED)

    def mark_analyses_deleted(self, case_id: str) -> Query:
        """mark analyses connected to a case as deleted"""
        old_analyses = self.analyses(case_id=case_id)
        if old_analyses.count() > 0:
            for old_analysis in old_analyses:
                old_analysis.is_deleted = True
            self.commit()
        return old_analyses

    def set_analysis_completed(self, analysis_id: int) -> None:
        """Set an analysis status to completed."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id=analysis_id)
        analysis.status = TrailblazerStatus.COMPLETED
        self.commit()
        LOG.info(f"{analysis.family} - status set to {TrailblazerStatus.COMPLETED}")

    def set_analysis_uploaded(self, case_id: str, uploaded_at: dt.datetime) -> None:
        """Setting analysis uploaded at."""
        analysis_obj: Analysis = self.get_latest_analysis(case_id=case_id)
        analysis_obj.uploaded_at: dt.datetime = uploaded_at
        self.commit()

    def set_analysis_status(self, case_id: str, status: str):
        """Setting analysis status."""
        status = status.lower()
        if status not in set(TrailblazerStatus.statuses()):
            raise ValueError(f"Invalid status. Allowed values are: {TrailblazerStatus.statuses()}")
        analysis_obj: Analysis = self.get_latest_analysis(case_id=case_id)
        analysis_obj.status: str = status
        self.commit()
        LOG.info(f"{analysis_obj.family} - Status set to {status.upper()}")

    def add_comment(self, case_id: str, comment: str):
        analysis_obj: Analysis = self.get_latest_analysis(case_id=case_id)
        analysis_obj.comment: str = (
            " ".join([analysis_obj.comment, comment]) if analysis_obj.comment else comment
        )

        self.commit()

        LOG.info(f"Adding comment {comment} to analysis {analysis_obj.family}")

    def delete_analysis(self, analysis_id: int, force: bool = False) -> None:
        """Delete the analysis output."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            raise TrailblazerError("Analysis not found")

        if not force and analysis.status in TrailblazerStatus.ongoing_statuses():
            raise TrailblazerError(
                f"Analysis for {analysis.family} is currently running! Use --force flag to delete anyway."
            )
        LOG.info(f"Deleting analysis {analysis_id} for case {analysis.family}")
        analysis.delete()
        self.commit()

    @staticmethod
    def query_slurm(job_id_file: str, case_id: str, ssh: bool) -> Any:
        """Args:
        job_id_file: Path to slurm id .YAML file as string
        case_id: Unique internal case identifier which is expected to by the only item in the .YAML dict
        ssh : Whether the request is executed from hasta or clinical-db"""
        job_id: dict = ReadFile.get_content_from_file(
            file_format=FileFormat.YAML, file_path=Path(job_id_file)
        )
        submitted_job_ids = job_id.get(next(iter(job_id)))
        job_ids_string = ",".join(map(str, submitted_job_ids))
        if ssh:
            return (
                subprocess.check_output(
                    [
                        "ssh",
                        "hiseq.clinical@hasta.scilifelab.se",
                        "squeue",
                        "-j",
                        job_ids_string,
                        "--states=all",
                        "-o",
                        "%A,%j,%T,%l,%M,%S",
                    ],
                    universal_newlines=True,
                )
                .decode("utf-8")
                .strip()
                .replace("//n", "/n")
            )
        else:
            return subprocess.check_output(
                [
                    "squeue",
                    "-j",
                    job_ids_string,
                    "--states=all",
                    "-o",
                    "%A,%j,%T,%l,%M,%S",
                ]
            ).decode("utf-8")

    def update_ongoing_analyses(self, ssh: bool = False) -> None:
        """Iterate over all analysis with ongoing status and query SLURM for current progress."""
        ongoing_analyses = self.analyses(temp=True)
        for analysis_obj in ongoing_analyses:
            try:
                self.update_run_status(analysis_id=analysis_obj.id, ssh=ssh)
            except Exception as error:
                LOG.error(
                    f"Failed to update {analysis_obj.family} - {analysis_obj.id}: {type(error).__name__}"
                )

    def update_run_status(self, analysis_id: int, ssh: bool = False) -> None:
        """Query entries related to given analysis, and update the Trailblazer database."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            LOG.warning(f"Analysis {analysis_id} not found!")
            return
        if analysis.workflow_manager == WorkflowManager.TOWER.value:
            self.update_tower_run_status(analysis_id=analysis_id)
        elif analysis.workflow_manager == WorkflowManager.SLURM.value:
            self.update_analysis_from_slurm_run_status(analysis_id=analysis_id, ssh=ssh)

    def update_analysis_from_slurm_run_status(self, analysis_id: int, ssh: bool = False) -> None:
        """Query slurm for entries related to given analysis, and update the analysis in the database."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id=analysis_id)
        try:
            squeue_result: SqueueResult = get_squeue_result(
                squeue_response=self.query_slurm(
                    job_id_file=analysis.config_path, case_id=analysis.family, ssh=ssh
                )
            )
            self.update_analysis_jobs_from_slurm_jobs(
                analysis=analysis, squeue_result=squeue_result
            )
            LOG.info(f"Status in SLURM: {analysis.family} - {analysis_id}")
            LOG.debug(squeue_result.jobs)
            analysis.progress = squeue_result.jobs_status_distribution.get(
                SlurmJobStatus.COMPLETED, 0.0
            )
            analysis.status = get_current_analysis_status(
                jobs_status_distribution=squeue_result.jobs_status_distribution
            )
            LOG.info(f"Updated status {analysis.family} - {analysis.id}: {analysis.status} ")
            self.commit()

            analysis.logged_at = dt.datetime.now()
        except Exception as exception:
            LOG.error(
                f"Error updating analysis for: case - {analysis.family} : {exception.__class__.__name__}"
            )
            analysis.status = TrailblazerStatus.ERROR
            self.commit()

    @staticmethod
    def query_tower(config_file: str, case_id: str) -> TowerAPI:
        """Parse a config file to extract a NF Tower workflow ID and return a TowerAPI.
        Currently only one tower ID is supported."""
        workflow_id: int = ReadFile.get_content_from_file(
            file_format=FileFormat.YAML, file_path=Path(config_file)
        ).get(case_id)[-1]
        tower_api = TowerAPI(workflow_id=workflow_id)
        if not tower_api.tower_client.meets_requirements:
            raise TowerRequirementsError
        return tower_api

    def update_tower_run_status(self, analysis_id: int) -> None:
        """Query tower for entries related to given analysis, and update the Trailblazer database."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id=analysis_id)
        tower_api: TowerAPI = self.query_tower(
            config_file=analysis.config_path, case_id=analysis.family
        )

        try:
            LOG.info(
                f"Status in Tower: {analysis.family} - {analysis_id} - {tower_api.workflow_id}"
            )
            analysis.status: str = tower_api.status
            analysis.progress: int = tower_api.progress
            analysis.logged_at: dt.datetime = dt.datetime.now()
            self.delete_analysis_jobs(analysis=analysis)
            self.update_analysis_jobs(
                analysis=analysis, jobs=tower_api.get_jobs(analysis_id=analysis.id)
            )
            self.commit()
            LOG.info(f"Updated status {analysis.family} - {analysis.id}: {analysis.status} ")
        except Exception as error:
            LOG.error(f"Error logging case - {analysis.family} :  {type(error).__name__}")
            analysis.status: str = TrailblazerStatus.ERROR
            self.commit()

    @staticmethod
    def cancel_slurm_job(slurm_id: int, ssh: bool = False) -> None:
        """Cancel slurm job by slurm job ID"""
        if ssh:
            subprocess.Popen(
                ["ssh", "hiseq.clinical@hasta.scilifelab.se", "scancel", str(slurm_id)]
            )
        else:
            subprocess.Popen(["scancel", str(slurm_id)])

    def cancel_analysis(self, analysis_id: int, email: str = None, ssh: bool = False) -> None:
        """Cancel all ongoing slurm jobs associated with the analysis, and set job status to canceled"""
        analysis: Analysis = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            raise TrailblazerError(f"Analysis {analysis_id} does not exist")

        if analysis.status not in TrailblazerStatus.ongoing_statuses():
            raise TrailblazerError(f"Analysis {analysis_id} is not running")

        for job_obj in analysis.failed_jobs:
            if job_obj.status in SlurmJobStatus.ongoing_statuses():
                LOG.info(f"Cancelling job {job_obj.slurm_id} - {job_obj.name}")
                self.cancel_slurm_job(job_obj.slurm_id, ssh=ssh)
        LOG.info(
            f"Case {analysis.family} - Analysis {analysis_id}: all ongoing jobs cancelled successfully!"
        )
        self.update_run_status(analysis_id=analysis_id)
        analysis.status = TrailblazerStatus.CANCELLED
        analysis.comment = (
            f"Analysis cancelled manually by user:"
            f" {(self.get_user(email=email).name if self.get_user(email=email) else (email or 'Unknown'))}!"
        )
        self.commit()


class Store(alchy.Manager, BaseHandler):
    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
