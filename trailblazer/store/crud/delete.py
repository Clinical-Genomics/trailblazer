import logging

from trailblazer.constants import TrailblazerStatus
from trailblazer.exc import TrailblazerError
from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import Analysis

LOG = logging.getLogger(__name__)


class DeleteHandler(BaseHandler_2):
    """Class for deleting items in the database."""

    def delete_analysis_jobs(self, analysis: Analysis) -> None:
        """Delete all jobs linked to the given analysis."""
        for job in analysis.jobs:
            job.delete()
        self.commit()

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
