import logging
from typing import Optional

from trailblazer.constants import TrailblazerStatus
from trailblazer.exc import MissingAnalysis, TrailblazerError
from trailblazer.store.base import BaseHandler
from trailblazer.store.models import Analysis

LOG = logging.getLogger(__name__)


class DeleteHandler(BaseHandler):
    """Class for deleting items in the database."""

    def delete_analysis_jobs(self, analysis: Analysis) -> None:
        """Delete all jobs linked to the given analysis."""
        for job in analysis.jobs:
            job.delete()
        self.commit()

    def delete_analysis(self, analysis_id: int, force: bool = False) -> None:
        """Delete the analysis from the database. Also delete ongoing analysis if 'force' is True.
        Raises:
            MissingAnalysis when no analysis.
            TrailblazerError for ongoing analysis for analysis id.
        """
        analysis: Optional[Analysis] = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            raise MissingAnalysis("Analysis not found")
        if not force and analysis.status in TrailblazerStatus.ongoing_statuses():
            raise TrailblazerError(
                f"Analysis for {analysis.family} is currently ongoing! Use --force flag to delete ongoing analysis."
            )
        LOG.info(f"Deleting analysis: {analysis_id}, for case: {analysis.family}")
        analysis.delete()
        self.commit()
