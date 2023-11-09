from datetime import datetime

from trailblazer.constants import TrailblazerStatus
from trailblazer.store.base import BaseHandler
from trailblazer.store.models import Analysis, User


class CreateHandler(BaseHandler):
    """Class for creating items in the database."""

    def add_pending_analysis(
        self,
        case_id: str,
        config_path: str,
        out_dir: str,
        priority: str,
        type: str,
        email: str = None,
        data_analysis: str = None,
        ticket_id: str = None,
        workflow_manager: str = None,
    ) -> Analysis:
        """Add pending analysis with user if supplied with email."""
        new_analysis: Analysis = Analysis(
            config_path=config_path,
            data_analysis=data_analysis,
            family=case_id,
            out_dir=out_dir,
            priority=priority,
            started_at=datetime.now(),
            status=TrailblazerStatus.PENDING.value,
            ticket_id=ticket_id,
            type=type,
            workflow_manager=workflow_manager,
        )
        new_analysis.user = self.get_user(email=email) if email else None
        self.add_commit(new_analysis)
        return new_analysis

    def add_user(self, name: str, email: str) -> User:
        """Add a new user to the database."""
        new_user: User = User(email=email, name=name)
        self.add_commit(new_user)
        return new_user
