"""Store backend in Trailblazer."""
import datetime as dt
import logging
import subprocess
from pathlib import Path
from typing import Optional

import alchy
import sqlalchemy as sqa
from alchy import Query

from trailblazer.apps.tower.api import TowerAPI
from trailblazer.constants import (
    FileFormat,
    SlurmJobStatus,
    TrailblazerStatus,
    WorkflowManager,
)
from trailblazer.exc import TowerRequirementsError, TrailblazerError
from trailblazer.io.controller import ReadFile
from trailblazer.store.core import CoreHandler
from trailblazer.store.models import Analysis, Model

LOG = logging.getLogger(__name__)


class BaseHandler(CoreHandler):
    Analysis = Analysis

    def setup(self):
        self.create_all()

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
        analysis: Optional[Analysis] = self.get_latest_analysis_for_case(case_name=case_id)
        analysis.uploaded_at = uploaded_at
        self.commit()

    def set_analysis_status(self, case_id: str, status: str):
        """Setting analysis status."""
        status: str = status.lower()
        if status not in set(TrailblazerStatus.statuses()):
            raise ValueError(f"Invalid status. Allowed values are: {TrailblazerStatus.statuses()}")
        analysis: Optional[Analysis] = self.get_latest_analysis_for_case(case_name=case_id)
        analysis.status = status
        self.commit()
        LOG.info(f"{analysis.family} - Status set to {status.upper()}")

    def add_comment(self, case_id: str, comment: str):
        analysis: Optional[Analysis] = self.get_latest_analysis_for_case(case_name=case_id)
        analysis.comment: str = (
            " ".join([analysis.comment, comment]) if analysis.comment else comment
        )
        self.commit()
        LOG.info(f"Adding comment {comment} to analysis {analysis.family}")

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

    def update_ongoing_analyses(self, use_ssh: bool = False) -> None:
        """Iterate over all analysis with ongoing status and query SLURM for current progress."""
        ongoing_analyses = self.analyses(temp=True)
        for analysis_obj in ongoing_analyses:
            try:
                self.update_run_status(analysis_id=analysis_obj.id, use_ssh=use_ssh)
            except Exception as error:
                LOG.error(
                    f"Failed to update {analysis_obj.family} - {analysis_obj.id}: {type(error).__name__}"
                )

    def update_run_status(self, analysis_id: int, use_ssh: bool = False) -> None:
        """Query entries related to given analysis, and update the Trailblazer database."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            LOG.warning(f"Analysis {analysis_id} not found!")
            return
        if analysis.workflow_manager == WorkflowManager.TOWER.value:
            self.update_tower_run_status(analysis_id=analysis_id)
        elif analysis.workflow_manager == WorkflowManager.SLURM.value:
            self.update_analysis_from_slurm_output(analysis_id=analysis_id, use_ssh=use_ssh)

    def update_analysis_from_slurm_output(self, analysis_id: int, use_ssh: bool = False) -> None:
        """Query SLURM for entries related to given analysis, and update the analysis in the database."""
        analysis: Optional[Analysis] = self.get_analysis_with_id(analysis_id=analysis_id)
        try:
            self._update_analysis_from_slurm_squeue_output(analysis=analysis, use_ssh=use_ssh)
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

        for job in analysis.jobs:
            if job.status in SlurmJobStatus.ongoing_statuses():
                LOG.info(f"Cancelling job {job.slurm_id} - {job.name}")
                self.cancel_slurm_job(job.slurm_id, ssh=ssh)
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
