from typing import List

from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import User, Analysis, Job


class UpdateHandler(BaseHandler_2):
    """Class for updating items in the database."""

    def add_user(self, name: str, email: str) -> User:
        """Add a new user to the database."""
        new_user: User = User(email=email, name=name)
        self.add_commit(new_user)
        return new_user

    def update_analysis_jobs(self, analysis: Analysis, jobs: List[dict]) -> None:
        """Update jobs in the analysis."""
        # failed_jobs is misnamed and actually contains all jobs irrespective of status
        analysis.failed_jobs = [Job(**job) for job in jobs]
        self.commit()

    def update_user_is_archived(self, user: User, archive: bool = True) -> None:
        """Update is archived fpr a user in the database."""
        user.is_archived = archive
        self.commit()
