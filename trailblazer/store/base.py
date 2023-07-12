from dataclasses import dataclass
from sqlalchemy import func
from sqlalchemy.orm import Query
from typing import Type

from trailblazer.store.models import Model, Job


@dataclass
class BaseHandler_2:
    """All models in one base class."""

    def __init__(self):
        pass

    def get_query(self, table: Type[Model]) -> Query:
        """Return a query for the given table."""
        return self.query(table)

    def get_job_query_with_name_and_count_labels(self) -> Query:
        """Return a Job query with a name label and a count with a label."""
        return self.session.query(
            Job.name.label("name"),
            func.count(Job.id).label("count"),
        )
