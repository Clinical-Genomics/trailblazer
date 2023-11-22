import logging

from sqlalchemy.orm import Session

from trailblazer.constants import TrailblazerStatus
from trailblazer.exc import MissingAnalysis, TrailblazerError
from trailblazer.store.base import BaseHandler
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis

LOG = logging.getLogger(__name__)


class DeleteHandler(BaseHandler):
    """Class for deleting items in the database."""

    def delete_analysis_jobs(self, analysis: Analysis) -> None:
        """Delete all jobs linked to the given analysis."""
        session: Session = get_session()
        for job in analysis.jobs:
            session.delete(job)
        session.commit()

    def delete_analysis(self, analysis_id: int, force: bool = False) -> None:
        """Delete the analysis from the database. Also delete ongoing analysis if 'force' is True.
        Raises:
            MissingAnalysis when no analysis.
            TrailblazerError for ongoing analysis for analysis id.
        """
        session: Session = get_session()
        analysis: Analysis | None = self.get_analysis_with_id(analysis_id=analysis_id)
        if not analysis:
            raise MissingAnalysis("Analysis not found")
        if not force and analysis.status in TrailblazerStatus.ongoing_statuses():
            raise TrailblazerError(
                f"Analysis for {analysis.family} is currently ongoing! Use --force flag to delete ongoing analysis."
            )
        LOG.info(f"Deleting analysis: {analysis_id}, for case: {analysis.family}")
        session.delete(analysis)
        session.commit()
