from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import Analysis


class DeleteHandler(BaseHandler_2):
    """Class for deleting items in the database."""

    def delete_analysis_jobs(self, analysis: Analysis) -> None:
        """Delete jobs in the Jobs table."""
        for job in analysis.failed_jobs:
            job.delete()
        self.commit()
