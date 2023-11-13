"""Utility functions to simply add test data in a Trailblazer store."""
from datetime import date, datetime
from sqlalchemy.orm import Session

from trailblazer.store.store import Store
from trailblazer.store.database import get_session
from trailblazer.store.models import Info, Job, User


class StoreHelpers:
    """Class to hold helper functions that needs to be used all over."""

    @staticmethod
    def add_info(store: Store) -> Info:
        """Add an info object to the store."""
        session: Session = get_session()
        info: Info = Info()
        session.add(info)
        return info

    @staticmethod
    def add_job(
        analysis_id: int,
        name: str,
        slurm_id: int,
        status: str,
        started_at: date = datetime.now(),
    ) -> Job:
        """Add an job object to the store."""
        session: Session = get_session()
        job: Job = Job(
            analysis_id=analysis_id,
            slurm_id=slurm_id,
            name=name,
            started_at=started_at,
            status=status,
        )
        session.add(job)
        return job

    @staticmethod
    def add_user(email: str, name: str, is_archived: bool = False) -> User:
        """Add a user object to the store."""
        session: Session = get_session()
        user = User(email=email, name=name, is_archived=is_archived)
        session.add(user)
        return user
