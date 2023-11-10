"""Utility functions to simply add test data in a Trailblazer store."""
from datetime import date, datetime

from trailblazer.store.core import Store
from trailblazer.store.models import Info, Job, User


class StoreHelpers:
    """Class to hold helper functions that needs to be used all over."""

    @staticmethod
    def add_info(store: Store) -> Info:
        """Add an info object to the store."""
        info: Info = Info()
        store.add(info)
        store.commit()
        return info

    @staticmethod
    def add_job(
        analysis_id: int,
        name: str,
        slurm_id: int,
        status: str,
        store: Store,
        started_at: date = datetime.now(),
    ) -> Job:
        """Add an job object to the store."""
        job: Job = Job(
            analysis_id=analysis_id,
            slurm_id=slurm_id,
            name=name,
            started_at=started_at,
            status=status,
        )
        store.add(job)
        store.commit()
        return job

    @staticmethod
    def add_user(email: str, name: str, store: Store, is_archived: bool = False) -> User:
        """Add a user object to the store."""
        user: User = User(email=email, name=name, is_archived=is_archived)
        store.add(user)
        store.commit()
        return user
