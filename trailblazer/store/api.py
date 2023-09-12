"""Store backend in Trailblazer."""
import datetime as dt
import logging
from pathlib import Path
from typing import Optional

import alchy
import sqlalchemy as sqa
from alchy import Query

from trailblazer.apps.tower.api import TowerAPI
from trailblazer.constants import FileFormat, TrailblazerStatus, WorkflowManager
from trailblazer.exc import TowerRequirementsError
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

    def update_ongoing_analyses(self, analysis_host: Optional[str] = None) -> None:
        """Iterate over all analysis with ongoing status and query SLURM for current progress."""
        ongoing_analyses = self.analyses(temp=True)
        for analysis_obj in ongoing_analyses:
            try:
                self.update_run_status(analysis_id=analysis_obj.id, analysis_host=analysis_host)
            except Exception as error:
                LOG.error(
                    f"Failed to update {analysis_obj.family} - {analysis_obj.id}: {type(error).__name__}"
                )

    def update_run_status(self, analysis_id: int, analysis_host: Optional[str] = None) -> None:
        """Query entries related to given analysis, and update the Trailblazer database."""
        analysis: Analysis = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            LOG.warning(f"Analysis {analysis_id} not found!")
            return
        if analysis.workflow_manager == WorkflowManager.TOWER.value:
            self.update_tower_run_status(analysis_id=analysis_id)
        elif analysis.workflow_manager == WorkflowManager.SLURM.value:
            self.update_analysis_from_slurm_output(
                analysis_id=analysis_id, analysis_host=analysis_host
            )

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


class Store(alchy.Manager, BaseHandler):
    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
