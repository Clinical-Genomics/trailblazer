from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import Analysis


class DeleteHandler(BaseHandler_2):
    """Class for deleting items in the database."""

    def delete_analysis_jobs(self, analysis: Analysis) -> None:
        """Delete all jobs linked to the given analysis."""
        for job in analysis.jobs:
            job.delete()
        self.commit()
